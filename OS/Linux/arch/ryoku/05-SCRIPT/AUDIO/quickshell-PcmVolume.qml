pragma Singleton

import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Services.Pipewire

// The internal speaker hotkeys adjust ALSA PCM instead of the PipeWire sink.
// Read that mixer control while the internal PCH output is selected so the
// QSbar readout reflects the level the user is actually changing.
Singleton {
    id: root

    readonly property var sink: Pipewire.defaultAudioSink
    readonly property string sinkName: sink && sink.name ? sink.name : ""
    readonly property bool usesPcm: sinkName.indexOf("alsa_output.pci-0000_00_1f.3.") === 0
    readonly property string card: Quickshell.env("RYOKU_PCM_CARD") || "PCH"

    property int pcmVolume: 0
    property bool pcmReady: false

    function refresh() {
        if (!root.usesPcm)
            return
        if (pcmRead.running) {
            readRetry.restart()
            return
        }
        pcmRead.running = true
    }

    onUsesPcmChanged: {
        root.pcmReady = false
        if (root.usesPcm)
            root.refresh()
    }
    Component.onCompleted: root.refresh()

    // ALSA mixer events leave a child process behind when Quickshell reloads.
    // A short-lived read keeps the indicator current without a persistent child.
    Timer {
        interval: 1000
        repeat: true
        running: root.usesPcm
        onTriggered: root.refresh()
    }

    Process {
        id: pcmRead
        command: ["amixer", "-c", root.card, "sget", "PCM"]
        stdout: StdioCollector {
            onStreamFinished: {
                const match = text.match(/Playback\s+\d+\s+\[(\d+(?:\.\d+)?)%\]/)
                if (root.usesPcm && match) {
                    root.pcmVolume = Math.round(Number(match[1]))
                    root.pcmReady = true
                }
            }
        }
    }
}
