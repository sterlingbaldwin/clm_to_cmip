import os, sys
import argparse
import cmor
import cdms2

from multiprocessing import Pool
from threading import Event
from importlib import import_module


class Cmorizer(object):
    """
    A utility class to cmorize clm time series files
    """
    def __init__(self, var_list, input_path, output_path, caseid, nproc=6, handlers='./cmor_handlers'):
        self._var_list = var_list
        self._input_path = input_path
        self._output_path = output_path
        self._nproc = nproc
        self._handlers_path = handlers
        self._caseid = caseid
        self._event = Event()
        self._pool = None
        self._pool_res = None
    
    def run(self):
        handlers = os.listdir(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                self._handlers_path))
        self._handlers = list()
        for handler in handlers:
            if not handler.endswith('.py'):
                continue
            if handler == "__init__.py":
                continue

            module, _ = handler.rsplit('.', 1)
            if module not in self._var_list:
                continue
            module_path = '.'.join([self._handlers_path, module])
            mod = import_module(module_path)
            met = getattr(mod, 'handle')
            self._handlers.append({module: met})
        
        print '--- printing handlers ---'
        for handler in self._handlers:
            for key, val in handler.items():
                print '\t' + val()

        print '\n--- calling handlers ---'
        print '--- running with {} processes ---'.format(self._nproc)
        self._pool = Pool(self._nproc)
        self._pool_res = list()

        for handler in self._handlers:
            for key, val in handler.items():
                kwds = {
                    'infile': os.path.join(
                                self._input_path, 
                                self._caseid + '.' + key + '.nc'),
                    'tables_dir': self._handlers_path
                }
                self._pool_res.append(
                    self._pool.apply_async(val, args=(), kwds=kwds))
        
        for res in self._pool_res:
            print res.get()
    
    def worker_wrapper(self, func, args):
        return func(**args)
    
    def terminate(self):
        if self._pool:
            self._pool.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--var-list',
        nargs='+', required=True,
        help='space seperated list of variables to convert from clm to cmip')
    parser.add_argument(
        '-c', '--caseid',
        required=True,
        help='name of case e.g. 20180129.DECKv1b_piControl.ne30_oEC.edison')
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='path to directory containing clm data with single variables per file')
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='where to store cmorized outputoutput')
    parser.add_argument(
        '-n', '--num-proc',
        default=6, type=int,
        help='optional: number of processes, default = 6')
    parser.add_argument(
        '-H', '--handlers',
        default='cmor_handlers',
        help='optional: path to cmor handlers directory, default = ./cmor_handlers')
    try:
        args = parser.parse_args(sys.argv[1:])
    except:
        parser.print_help()
        sys.exit(1)
    
    cmorizer = Cmorizer(
        var_list=args.var_list,
        input_path=args.input,
        output_path=args.output,
        caseid=args.caseid,
        nproc=args.num_proc,
        handlers=args.handlers)
    try:
        cmorizer.run()
    except KeyboardInterrupt as e:
        print '--- caught keyboard kill event ---'
        cmorizer.terminate()
    