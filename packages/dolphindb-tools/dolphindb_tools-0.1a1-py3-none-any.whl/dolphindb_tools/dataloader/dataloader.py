import copy
import random
from queue import Empty, Full, Queue
from threading import Event, Thread
from typing import List, Optional, Union

import torch
from dolphindb import session as Session

from .config import TIMEOUT
from .datamanager import DataManager
from .datasource import DataRealSource
from .helper import DataIndexHelper, RandomSampleHelper
from .utils import (MetaSQL, SequentialSession, _generate_tablename,
                    make_MetaSQL)


class DDBDataLoader(object):
    def __init__(
        self,
        ddbSession: Session,
        sql: str,
        targetCol: List[str],
        batchSize: int = 1,
        shuffle: bool = False,
        windowSize: Union[List[int], int, None] = None,
        windowStride: Union[List[int], int, None] = None,
        *,
        inputCol: Optional[List[str]] = None,
        excludeCol: Optional[List[str]] = None,
        repartitionCol: str = None,
        repartitionScheme: List[str] = None,
        groupCol: str = None,
        groupScheme: List[str] = None,
        seed: Optional[int] = None,
        dropLast: bool = False,
        offset: int = None,
        device: str = "cpu",
        prefetchBatch: int = 1,
        prepartitionNum: int = 2,
        groupPoolSize: int = 3,
        **kwargs
    ):
        if not isinstance(ddbSession, Session):
            raise TypeError("The type of ddbSession must be dolphindb.Session.")
        self.s: Session = SequentialSession(ddbSession)

        if groupCol is not None and not isinstance(groupCol, str):
            raise TypeError("The type of groupCol must be str.")
        self.group_col = groupCol
        self.group_scheme = groupScheme

        if repartitionCol is not None and not isinstance(repartitionCol, str):
            raise TypeError("The type of repartitionCol must be str.")
        self.repartition_col = repartitionCol
        self.repartition_scheme = repartitionScheme

        self.device = device

        if not isinstance(prefetchBatch, int):
            raise TypeError("The type of prefetchBatch must be str.")
        if prefetchBatch <= 0:
            raise ValueError("The value of prefetchBatch must be greater than 0.")
        self.prefetch = prefetchBatch

        if not isinstance(prepartitionNum, int):
            raise TypeError("The type of prepartitionNum must be str.")
        if prepartitionNum <= 0:
            raise ValueError("The value of prepartitionNum must be greater than 0.")
        self.prepartition_num = prepartitionNum

        if not isinstance(groupPoolSize, int):
            raise TypeError("The type of groupPoolSize must be str.")
        if groupPoolSize <= 0:
            raise ValueError("The value of groupPoolSize must be greater than 0.")
        self.grouppool_size = groupPoolSize

        if not isinstance(sql, str):
            raise TypeError("The type of sql must be str.")
        sql = make_MetaSQL(ddbSession, sql)
        sqls = self._take_group_effect(groupCol, groupScheme, sql)
        self.sqls = self._take_repartition_effect(repartitionCol, repartitionScheme, sqls)

        if windowSize is None:
            self.window_size = [None, None]
        elif isinstance(windowSize, int):
            self.window_size = [windowSize, 1]
        elif isinstance(windowSize, list):
            if len(windowSize) != 2:
                raise ValueError("windowSize must be like int or [int, int].")
            self.window_size = windowSize
        else:
            raise ValueError("windowSize must be like int or [int, int].")

        if windowStride is None:
            self.window_stride = [None, None]
        elif isinstance(windowStride, int):
            self.window_stride = [windowStride, 1]
        elif isinstance(windowStride, list):
            if len(windowStride) != 2:
                raise ValueError("windowStride must be like int or [int, int].")
            self.window_stride = windowStride
        else:
            raise ValueError("windowStride must be like int or [int, int].")

        if offset is None:
            if self.window_size[0] is not None:
                offset = self.window_size[0]
            else:
                offset = 0
        if not isinstance(offset, int):
            raise TypeError("The type of offset must be int.")
        if offset < 0:
            raise ValueError("The value of offset must not be less than 0.")
        self.offset = offset

        if not isinstance(batchSize, int):
            raise TypeError("The type of batchSize must be int.")
        if batchSize <= 0:
            raise ValueError("The value of batchSize must be greater than 0.")
        self.batch_size = batchSize

        self.shuffle = shuffle
        self.drop_last = dropLast

        if inputCol is not None:
            if isinstance(inputCol, str):
                inputCol = [inputCol]
            if not isinstance(inputCol, list):
                raise TypeError("The type of inputCol must be str or List[str].")
        self.input_cols = inputCol

        if targetCol is None:
            raise ValueError("Parameter targetCol must be specified.")
        if isinstance(targetCol, str):
            targetCol = [targetCol]
        if not isinstance(targetCol, list):
            raise TypeError("The type of targetCol must be str or List[str].")
        self.target_cols = targetCol

        if excludeCol is not None:
            if isinstance(excludeCol, str):
                excludeCol = [excludeCol]
            if not isinstance(excludeCol, list):
                raise TypeError("The type of excludeCol must be str or List[str].")
        self.exclude_cols = excludeCol if excludeCol is not None else []

        if "verbose" in kwargs:
            self.verbose = bool(kwargs["verbose"])
        else:
            self.verbose = False

        self.seed = seed
        self.random_ins = random.Random(seed)
        self._define_helper_func()
        self.release_flag = False
        self.dms = self.sqls

    def _take_group_effect(self, group_col, group_scheme, sql: MetaSQL):
        if group_col is None and group_scheme is None:
            return [sql]
        if not (group_col and group_scheme):
            raise ValueError("Both groupCol and groupScheme must be specified simultaneously.")
        if not isinstance(group_col, str):
            raise TypeError("groupCol must be str.")
        if not isinstance(group_scheme, list):
            raise TypeError("groupScheme must be list.")
        res_sqls = []
        for scheme in group_scheme:
            scheme = str(scheme)
            res_sql = copy.deepcopy(sql)
            res_sql.add_where([f"< {group_col} = {scheme} >"])
            res_sqls.append(res_sql)
        return res_sqls

    def _take_repartition_effect(self, repartition_col, repartition_scheme, sqls):
        if repartition_col is None and repartition_scheme is None:
            return [[sql] for sql in sqls]
        if not (repartition_col and repartition_scheme):
            raise ValueError("Both repartitionCol and repartitionScheme must be specified simultaneously.")
        if not isinstance(repartition_col, str):
            raise TypeError("repartitionCol must be str.")
        if not isinstance(repartition_scheme, list):
            raise TypeError("repartitionScheme must be list.")
        res_sqls = [[] for _ in range(len(sqls))]
        for i, sql in enumerate(sqls):
            for scheme in repartition_scheme:
                res_sql = copy.deepcopy(sql)
                res_sql.add_where([f"< {repartition_col} = {scheme} >"])
                res_sqls[i].append(res_sql)
        return res_sqls

    def _define_helper_func(self):
        self.func_name = _generate_tablename("UTIL_HELPER")
        self.s.run("""
            def """ + f"{self.func_name}" + """(sql){
                tmp = sqlDS(sql, true);
                length = size tmp;
                if(length == 0){return NULL}
                counts = array(LONG, length);
                for(i in 0..(length-1)){
                    counts[i] = exec * from tmp[i]
                }
                return counts
            }
        """)

    def __del__(self):
        try:
            self.release()
        except Exception:
            pass

    def release(self):
        if not self.release_flag:
            self.s.run(f"undef('{self.func_name}', DEF);")
            self.release_flag = True

    def __iter__(self):
        if self.seed is None:
            new_seed = self.random_ins.randint(0, 10000)
            self.random_ins.seed(new_seed)
            self.new_seed = new_seed
        else:
            self.random_ins.seed(self.seed)
        self.queue = Queue(self.prefetch)
        self.dm_queue = Queue(1)
        self.back_thread = Thread(target=self._prepare_next_batch)
        self.back_thread.start()
        return self._get_next_batch_data()

    def _get_next_batch_data(self):
        while True:
            ndata = self.queue.get()
            self.queue.task_done()
            if ndata is None:
                break
            elif isinstance(ndata, Exception):
                raise ndata
            x, y = ndata
            if self.window_size[0] is None:
                x = torch.squeeze(x, dim=1)
            if self.window_size[1] is None:
                y = torch.squeeze(y, dim=1)
            yield x, y
        self.back_thread.join()

    def _prepare_next_batch(self):
        try:
            dm_pool_size = self.grouppool_size
            dms = copy.deepcopy(self.dms)
            exit_flag = Event()
            self.dm_thread = Thread(target=self._prepare_next_data_manager, args=(dms, exit_flag))
            self.dm_thread.start()
            dm_iter = self._get_next_data_manager(len(self.dms), exit_flag)

            generators = [next(dm_iter) for _ in range(min(len(self.dms), dm_pool_size))]

            data_rows = [[], []]
            all_flag = True
            while len(generators) != 0:
                ndata = []
                try:
                    if self.shuffle:
                        random_generator = self.random_ins.choice(generators)
                    else:
                        random_generator = generators[0]
                    data_row = [next(dm) for dm in random_generator]
                    for i, data in enumerate(data_row):
                        data_rows[i].append(data)
                        if len(data_rows[i]) >= self.batch_size:
                            ndata.append(torch.stack([_.data for _ in data_rows[i]]))
                            data_rows[i] = []
                    if len(ndata) > 0:
                        self.queue.put(ndata)
                except StopIteration:
                    generators.remove(random_generator)
                    if all_flag:
                        try:
                            new_generator = next(dm_iter)
                            generators.append(new_generator)
                        except StopIteration:
                            all_flag = False
            if len(data_rows[0]) and not self.drop_last:
                ndata = []
                for data in data_rows:
                    ndata.append(torch.stack([_.data for _ in data]))
                self.queue.put(ndata)
            self.queue.put(None)
            self.dm_thread.join()
        except Exception as e:
            exit_flag.set()
            self.queue.put(e)
            self.dm_thread.join()

    def _prepare_next_data_manager(self, dms, exit_flag: Event):
        if self.seed is None:
            seed = self.new_seed
        else:
            seed = self.seed
        try:
            while len(dms) > 0 and not exit_flag.is_set():
                if self.shuffle:
                    sql_sample = self.random_ins.sample(dms, k=1)[0]
                else:
                    sql_sample = dms[0]
                dms.remove(sql_sample)
                dm_pair = self._create_data_manager(sql_sample, seed)
                dm = self._start_data_manager(dm_pair, exit_flag)

                put_flag = False
                while not put_flag and not exit_flag.is_set():
                    try:
                        self.dm_queue.put(dm, timeout=TIMEOUT)
                        put_flag = True
                    except Full:
                        pass
        except Exception as e:
            put_flag = False
            while not put_flag and not exit_flag.is_set():
                try:
                    self.dm_queue.put(e, timeout=TIMEOUT)
                    put_flag = True
                except Full:
                    pass

    def _get_next_data_manager(self, all_len, exit_flag: Event):
        while all_len and not exit_flag.is_set():
            get_flag = False
            while not get_flag and not exit_flag.is_set():
                try:
                    dm = self.dm_queue.get(timeout=TIMEOUT)
                    get_flag = True
                    if isinstance(dm, Exception):
                        raise dm
                    else:
                        yield dm
                    self.dm_queue.task_done()
                    all_len -= 1
                except Empty:
                    pass

    def _create_data_manager(self, sqls, seed):
        input_window_size = self.window_size[0] if self.window_size[0] is not None else 1
        target_window_size = self.window_size[1] if self.window_size[1] is not None else 1
        input_window_stride = self.window_stride[0] if self.window_stride[0] is not None else 1
        target_window_stride = self.window_stride[1] if self.window_stride[1] is not None else 1

        ds_input = DataRealSource(
            self.s, sqls,
            "INPUT", self.func_name,
            input_cols=self.input_cols,
            target_cols=self.target_cols,
            exclude_cols=self.exclude_cols,
            offset=0, device=self.device,
            q_size=self.prepartition_num,
            verbose=self.verbose,
        )
        ds_target = DataRealSource(
            self.s, sqls,
            "TARGET", self.func_name,
            input_cols=self.input_cols,
            target_cols=self.target_cols,
            exclude_cols=self.exclude_cols,
            offset=self.offset, device=self.device,
            q_size=self.prepartition_num,
            verbose=self.verbose,
        )
        data_num_input = (ds_input.data_len() - input_window_size) // input_window_stride + 1
        data_num_target = (ds_target.data_len() - target_window_size) // target_window_stride + 1

        if self.shuffle and data_num_input <= data_num_target:
            p_sampler = [_ for _ in RandomSampleHelper(len(ds_input), seed=seed)]
            index_list = DataIndexHelper(
                ds_input.prefix_sum, p_sampler,
                self.window_size[0], self.window_stride[0],
                seed=seed,
            )
        elif self.shuffle:
            p_sampler = [_ for _ in RandomSampleHelper(len(ds_target), seed=seed)]
            index_list = DataIndexHelper(
                ds_target.prefix_sum, p_sampler,
                self.window_size[1], self.window_stride[1],
                seed=seed,
            )
        else:
            index_list = [_ for _ in range(min(data_num_input, data_num_target))]
        return [
            (ds_input, index_list, self.window_size[0], self.window_stride[0]),
            (ds_target, index_list, self.window_size[1], self.window_stride[1]),
        ]

    def _start_data_manager(self, dm_pair, exit_flag: Event):
        dms = []
        for dm_msg in dm_pair:
            ds, index, wsize, wstride = dm_msg
            dm = DataManager(ds, index, wsize, wstride, exit_flag=exit_flag)
            dm.start()
            dms.append(iter(dm))
        return dms
