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

const AirPlayIcon = () => (
  <svg
    viewBox="0 0 46 46"
    width="20"
    height="20"
    style={{
      width: "20px",
      height: "20px",
      display: "inline-block",
      verticalAlign: "middle",
      fill: "currentColor"
    }}
  >
    <path d="M22.24 28.66 8.63 44.35c-.56.65-.1 1.66.76 1.66h27.22c.86 0 1.32-1.01.76-1.66L23.76 28.66a.999.999 0 0 0-1.51 0Z"/>
    <path d="M15 23c0-4.41 3.59-8 8-8s8 3.59 8 8c0 2.64-1.29 4.97-3.26 6.43l1.64 1.89c2.5-1.92 4.12-4.93 4.12-8.33 0-5.8-4.7-10.5-10.5-10.5S12.5 17.2 12.5 23c0 3.4 1.62 6.41 4.12 8.33l1.64-1.89C16.29 27.97 15 25.64 15 23Z"/>
    <path d="M9 23c0-7.72 6.28-14 14-14s14 6.28 14 14c0 4.44-2.09 8.4-5.33 10.97l1.65 1.9c3.77-3.02 6.18-7.66 6.18-12.86 0-9.11-7.39-16.5-16.5-16.5S6.5 13.89 6.5 23c0 5.2 2.42 9.84 6.18 12.86l1.65-1.9C11.09 31.4 9 27.44 9 23Z"/>
    <path d="M2.5 23C2.5 11.7 11.7 2.5 23 2.5S43.5 11.7 43.5 23c0 6.4-2.95 12.12-7.56 15.88l1.65 1.9C42.73 36.56 46 30.16 46 23 46 10.3 35.7 0 23 0S0 10.3 0 23c0 7.16 3.27 13.56 8.41 17.78l1.65-1.9C5.45 35.12 2.5 29.4 2.5 23Z"/>
  </svg>
);

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
  const toastListener = (data: any) => {
    if (serverApi?.toaster?.toast) {
      serverApi.toaster.toast({
        title: data.title,
        body: data.message,
        duration: 4000
      });
    }
  };

  const unregister = serverApi?.on ? serverApi.on("show_toast", toastListener) : undefined;

  return {
    title: <div className="AirPlayTitle">AirPlay</div>,
    content: <AirPlayPanel serverApi={serverApi} />,
    icon: <AirPlayIcon />,
    onDismount() {
      if (typeof unregister === "function") {
        unregister();
      }
    },
  };
});