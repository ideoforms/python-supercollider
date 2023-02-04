(
SynthDef("sine", { arg freq=800;
    var osc;
    osc = SinOsc.ar(freq, 0, 0.1); // 800 Hz sine oscillator
    Out.ar(0, osc); // send output to audio bus zero.
}).store; // write the def to disk in the default directory synthdefs/
)
(
~sendAddr = NetAddr.new("127.0.0.1", 57901);
~sendAddr.sendMsg("/synced", "Nailed.")
);
s.sendMsg("/sync", )
s.sendMsg("/dumpOSC", 0)
s.boot
s.quit

NetAddr.langPort
s.status
OSCFunc.trace
OSCFunc.trace(false)

s.boot
s.quit
n = Synth("default");
n.free;
n = s.nextNodeID
s.sendMsg("/s_new", "default", n);
s.sendMsg("/n_free", n);
s.sendMsg("/sync", 1)