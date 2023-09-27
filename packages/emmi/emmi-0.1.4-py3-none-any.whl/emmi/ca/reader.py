#!/usr/bin/python3

import asyncio, time

from caproto.sync import client as ca_client
import numpy as np

from xarray import DataArray

class PvRetry(RuntimeError):
    '''
    Raised by GuidedPvReader when the PVs are not yet ready / guide does
    not yet signal readiness for signal readout.
    '''
    def __init__(self, *p, **kw):
        super().__init__(*p, **kw)


#def pv2xa(pvname, unpackScalar=False):
#    '''
#    '''
#    ca_client.read(self.prefix+k)    
#    pass


class GuidedPvReader:
    '''
    Observes a "guide" variable to determine when a specific EPICS PV signal is
    available, then collects the PV signal (which can come in a list of other PVs).
    '''

    def __init__(self, pv=None, guides=None, prefix=''):
        '''
        Initialises the reader. Parameters:
        
          - `pv`: A single PV, or a list of PVs, to read out. If not
            specified here, it can be specified later.
        
          - `guides`: A dicitonary of guide variable(s) and their respective
            value to use. The `pv` values will be acquired on the first occasion
            when *all* of the guides' values have changed *to* the value specified
            in the dictionary. If the dictionary value is a callable, it will be
            called with the guide value as its sole parameter and the `pv` value
            will be obtained the first time the return value changes to `True`.

          - `prefix`: If specified, it will be prepended to all of the
            PVs' and guides' EPICS names.
        '''

        self.prefix = prefix or ''
        self.pv = tuple([ i for i in (pv or []) ])
        self.guides = { prefix+k: v if hasattr(v, "__call__") else lambda x: x == v \
                        for k,v in guides.items() }
        self.guide_evals = { k:None for k in self.guides }
        

    def extract_data(self, response, pvName=None):
        '''
        Extracts "useful" data out of a response telegram.
        '''
        if response.data_type == ca_client.ChannelType.STRING:
            return response.data[0].decode('utf-8')
        elif response.data_type in (ca_client.ChannelType.DOUBLE, ):
            if len(response.data) == 1:
                return response.data[0]

            if not pvName or not pvName.endswith("_SIGNAL"):
                return response.data
            
            # If we have an array and it ends on _SIGNAL, we also try to
            # load _OFFSET and _DELTA for intrinsic scaling information
            axis = None
            try:
                offs = self.extract_data(ca_client.read(pvName.replace("_SIGNAL", "_OFFSET")))
                dlta = self.extract_data(ca_client.read(pvName.replace("_SIGNAL", "_DELTA")))
                
                axis = offs+np.array(range(len(response.data)))*dlta
            
            except Exception as e:
                #print("Reading %r: %r" % (pvName, str(e)))
                axis = np.array(range(len(response.data)))
                
            return DataArray(data=response.data, dims=["x"], coords=[axis])
            
        else:
            logging.warning ("Unhandled data type: %r" % (response.response.data_type,))
            return response.data[0]

    
    def retr(self, pv=None, raiseRetry=True):
        '''
        Checks the guides for readiness and retrieves the value(s) of the PV(s).
        If `pv` is not `None`, they will be retrieved in addition to the ones
        already specified at the initialisation of the class. If `prefix` is
        specified (not `None`), it will override whatever was specified at the
        initialisation of the class, but only for the PVs specified here.
        '''

        good_guides = 0

        for (k,v) in self.guides.items():
            data = self.extract_data(ca_client.read(k))
            #print ("guide evals:", self.guide_evals, "current eval:", v(data))
            if v(data) and (not self.guide_evals[k]):
                good_guides += 1
            self.guide_evals[k] = v(data)

        if good_guides == len(self.guides):
            pv = [k for k in (pv or {}) ]
            pv.extend([k for k in self.pv])
            return { k: self.extract_data(ca_client.read(self.prefix+k), pvName=self.prefix+k) \
                     for k in pv }

        raise PvRetry()


    async def value(self, timeout=-1, pollPeriod=0.001):
        '''
        Asynchronousluy waits for retr() to deliver a valid dataset.
        Cancels after `timeout` seconds (if timeout >= 0).
        '''
        tstart = time.time()
        while True:
            try:
                return self.retr()
            except PvRetry:
                if (timeout > 0) and (time.time()-tstart >= timeout):
                    raise
            await asyncio.sleep(pollPeriod)
