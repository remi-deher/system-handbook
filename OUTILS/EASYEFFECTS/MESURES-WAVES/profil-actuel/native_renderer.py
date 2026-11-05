"""Independent shared-mode WASAPI renderer with explicit stream category.
No capture interface and no microphone. Caller must keep physical output muted.
"""
import ctypes,time
from ctypes import POINTER,HRESULT,c_uint32,c_longlong,c_int,c_ubyte
from ctypes.wintypes import BOOL,DWORD
from comtypes import COMMETHOD,GUID,IUnknown,CLSCTX_ALL
from pycaw.api.audioclient import IAudioClient
from pycaw.api.audioclient.depend import WAVEFORMATEX
import numpy as np
class AudioClientProperties(ctypes.Structure):
    _fields_=[('cbSize',c_uint32),('bIsOffload',BOOL),('eCategory',c_int),('Options',DWORD)]
class IAudioClient2(IAudioClient):
    _iid_=GUID('{726778CD-F60A-4eda-82DE-E47610CD78AA}')
    _methods_=[COMMETHOD([],HRESULT,'IsOffloadCapable',(['in'],c_int,'category'),(['out'],POINTER(BOOL),'capable')),
               COMMETHOD([],HRESULT,'SetClientProperties',(['in'],POINTER(AudioClientProperties),'properties')),
               COMMETHOD([],HRESULT,'GetBufferSizeLimits',(['in'],POINTER(WAVEFORMATEX),'format'),(['in'],BOOL,'eventDriven'),(['out'],POINTER(c_longlong),'minimum'),(['out'],POINTER(c_longlong),'maximum'))]
class IAudioRenderClient(IUnknown):
    _iid_=GUID('{F294ACFC-3146-4483-A7BF-ADDCA7C260E2}')
    _methods_=[COMMETHOD([],HRESULT,'GetBuffer',(['in'],c_uint32,'frames'),(['out'],POINTER(POINTER(c_ubyte)),'buffer')),
               COMMETHOD([],HRESULT,'ReleaseBuffer',(['in'],c_uint32,'frames'),(['in'],DWORD,'flags'))]
def play(device,x,rate,category,safety_check):
    client=device._dev.Activate(IAudioClient2._iid_,CLSCTX_ALL,None).QueryInterface(IAudioClient2)
    props=AudioClientProperties(ctypes.sizeof(AudioClientProperties),False,category,0)
    client.SetClientProperties(ctypes.byref(props));fmt=client.GetMixFormat();started=False
    try:
        f=fmt.contents
        if f.nChannels!=2 or f.nSamplesPerSec!=rate or f.wBitsPerSample!=32:raise RuntimeError('Native mix format is not 48k stereo float32')
        raw_format=ctypes.string_at(fmt,18+f.cbSize).hex()
        if not (f.wFormatTag==3 or (f.wFormatTag==65534 and bytes.fromhex(raw_format)[24:28]==b'\x03\0\0\0')):raise RuntimeError('Expected IEEE float format/subtype')
        client.Initialize(0,0,1000000,0,fmt,None)
        render=client.GetService(ctypes.byref(IAudioRenderClient._iid_)).QueryInterface(IAudioRenderClient)
        capacity=client.GetBufferSize();x=np.ascontiguousarray(x,dtype='float32');position=0;underruns=0;deadline=time.monotonic()+len(x)/rate+10
        while position<len(x):
            safety_check()
            padding=client.GetCurrentPadding();available=capacity-padding
            if available>0:
                count=min(available,len(x)-position);target=render.GetBuffer(count)
                ctypes.memmove(target,x.ctypes.data+position*8,count*8);render.ReleaseBuffer(count,0);position+=count
                if not started:client.Start();started=True
                elif padding==0:underruns+=1
            else:time.sleep(.002)
            if time.monotonic()>deadline:raise RuntimeError('Native renderer timed out')
        while client.GetCurrentPadding()>0:
            safety_check();time.sleep(.002)
            if time.monotonic()>deadline:raise RuntimeError('Native renderer drain timed out')
        return dict(renderer='IAudioClient2 direct, shared, non-offloaded, Options NONE',category=category,buffer_frames=capacity,detected_empty_buffer_events=underruns,raw_mix_format=raw_format)
    finally:
        if started:client.Stop()
        ctypes.windll.ole32.CoTaskMemFree(fmt)
