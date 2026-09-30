import React, { useState, useEffect } from "react";
import {
  definePlugin,
  PanelSection,
  PanelSectionRow,
  TextField,
  ToggleField,
  DropdownItem,
  ButtonItem
} from "@decky/ui";
import { FaBroadcastTower } from "react-icons/fa";

interface NowPlayingData {
  device?: string;
  artist: string;
  title: string;
  cover?: string | null;
}

const AirPlayPanel = ({ serverApi }: { serverApi: any }) => {
  const [serverName, setServerName] = useState("");
  const [fps, setFps] = useState(60);
  const [avdec, setAvdec] = useState(true);
  const [pin, setPin] = useState(true);
  const [customArgs, setCustomArgs] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    serverApi.callPluginMethod("get_settings", {}).then((res: any) => {
      if (res.result) {
        setServerName(res.result.server_name || "");
        setFps(res.result.fps || 60);
        setAvdec(res.result.avdec ?? true);
        setPin(res.result.pin ?? true);
        setCustomArgs(res.result.custom_args || "");
      }
    });

    const unregisterMirroring = serverApi.routerHook?.addNotificationListener(
      "screen_mirroring",
      (data: { device: string }) => {
        serverApi.toaster?.toast({
          title: `${data.device || "Apple Device"} — Screen Mirroring`,
          body: "Mirroring session started",
          duration: 3500,
          playSound: false,
        });
      }
    );

    const unregisterAudio = serverApi.routerHook?.addNotificationListener(
      "now_playing",
      (data: NowPlayingData) => {
        const artist = data.artist || "Unknown Artist";
        const title = data.title || "Unknown Track";

        serverApi.toaster?.toast({
          title: `${data.device || "Apple Device"} — Now Playing`,
          body: `${artist} — ${title}`,
          duration: 4000,
          playSound: false,
          icon: data.cover ? (
            <img
              src={data.cover}
              style={{
                width: "44px",
                height: "44px",
                borderRadius: "6px",
                objectFit: "cover",
                marginRight: "6px"
              }}
            />
          ) : undefined
        });
      }
    );

    return () => {
      if (unregisterMirroring) unregisterMirroring();
      if (unregisterAudio) unregisterAudio();
    };
  }, []);

  const saveSettings = async (overrides: any = {}) => {
    const payload = {
      server_name: overrides.server_name ?? serverName,
      fps: overrides.fps ?? fps,
      avdec: overrides.avdec ?? avdec,
      pin: overrides.pin ?? pin,
      custom_args: overrides.custom_args ?? customArgs
    };
    await serverApi.callPluginMethod("update_settings", { new_settings: payload });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <PanelSection title="AirPlay Settings">
      <PanelSectionRow>
        <TextField
          label="Device Name"
          value={serverName}
          onChange={(e) => setServerName(e.target.value)}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <DropdownItem
          label="Frame Rate (FPS)"
          menuLabel="FPS"
          rgOptions={[
            { data: 60, label: "60 FPS (Smooth)" },
            { data: 30, label: "30 FPS (Power Saving)" }
          ]}
          selectedOption={fps}
          onChange={(newFps: any) => {
            setFps(newFps.data);
            saveSettings({ fps: newFps.data });
          }}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <ToggleField
          label="Hardware Decoder (-avdec)"
          description="GPU/libav accelerated decoding"
          checked={avdec}
          onChange={(val) => {
            setAvdec(val);
            saveSettings({ avdec: val });
          }}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <ToggleField
          label="Require PIN (-p)"
          description="Enforce one-time pairing code"
          checked={pin}
          onChange={(val) => {
            setPin(val);
            saveSettings({ pin: val });
          }}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <TextField
          label="Custom Arguments"
          description="Extra UxPlay launch flags"
          value={customArgs}
          onChange={(e) => setCustomArgs(e.target.value)}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={() => saveSettings()}>
          {saved ? "Saved!" : "Apply Settings"}
        </ButtonItem>
      </PanelSectionRow>
    </PanelSection>
  );
};

export default definePlugin((serverApi: any) => {
  return {
    title: <div className="AirPlayTitle">AirPlay</div>,
    content: <AirPlayPanel serverApi={serverApi} />,
    icon: <FaBroadcastTower />
  };
});