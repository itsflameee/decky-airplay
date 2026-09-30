var plugin = (function (React, ui) {
  'use strict';

  var DefaultContext = {
    color: undefined,
    size: undefined,
    className: undefined,
    style: undefined,
    attr: undefined
  };
  var IconContext = React.createContext && React.createContext(DefaultContext);

  var __assign = window && window.__assign || function () {
    __assign = Object.assign || function (t) {
      for (var s, i = 1, n = arguments.length; i < n; i++) {
        s = arguments[i];
        for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
      }
      return t;
    };
    return __assign.apply(this, arguments);
  };
  var __rest = window && window.__rest || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0) t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function") for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
      if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i])) t[p[i]] = s[p[i]];
    }
    return t;
  };
  function Tree2Element(tree) {
    return tree && tree.map(function (node, i) {
      return React.createElement(node.tag, __assign({
        key: i
      }, node.attr), Tree2Element(node.child));
    });
  }
  function GenIcon(data) {
    // eslint-disable-next-line react/display-name
    return function (props) {
      return React.createElement(IconBase, __assign({
        attr: __assign({}, data.attr)
      }, props), Tree2Element(data.child));
    };
  }
  function IconBase(props) {
    var elem = function (conf) {
      var attr = props.attr,
        size = props.size,
        title = props.title,
        svgProps = __rest(props, ["attr", "size", "title"]);
      var computedSize = size || conf.size || "1em";
      var className;
      if (conf.className) className = conf.className;
      if (props.className) className = (className ? className + " " : "") + props.className;
      return React.createElement("svg", __assign({
        stroke: "currentColor",
        fill: "currentColor",
        strokeWidth: "0"
      }, conf.attr, attr, svgProps, {
        className: className,
        style: __assign(__assign({
          color: props.color || conf.color
        }, conf.style), props.style),
        height: computedSize,
        width: computedSize,
        xmlns: "http://www.w3.org/2000/svg"
      }), title && React.createElement("title", null, title), props.children);
    };
    return IconContext !== undefined ? React.createElement(IconContext.Consumer, null, function (conf) {
      return elem(conf);
    }) : elem(DefaultContext);
  }

  // THIS FILE IS AUTO GENERATED
  function FaBroadcastTower (props) {
    return GenIcon({"attr":{"viewBox":"0 0 640 512"},"child":[{"tag":"path","attr":{"d":"M150.94 192h33.73c11.01 0 18.61-10.83 14.86-21.18-4.93-13.58-7.55-27.98-7.55-42.82s2.62-29.24 7.55-42.82C203.29 74.83 195.68 64 184.67 64h-33.73c-7.01 0-13.46 4.49-15.41 11.23C130.64 92.21 128 109.88 128 128c0 18.12 2.64 35.79 7.54 52.76 1.94 6.74 8.39 11.24 15.4 11.24zM89.92 23.34C95.56 12.72 87.97 0 75.96 0H40.63c-6.27 0-12.14 3.59-14.74 9.31C9.4 45.54 0 85.65 0 128c0 24.75 3.12 68.33 26.69 118.86 2.62 5.63 8.42 9.14 14.61 9.14h34.84c12.02 0 19.61-12.74 13.95-23.37-49.78-93.32-16.71-178.15-.17-209.29zM614.06 9.29C611.46 3.58 605.6 0 599.33 0h-35.42c-11.98 0-19.66 12.66-14.02 23.25 18.27 34.29 48.42 119.42.28 209.23-5.72 10.68 1.8 23.52 13.91 23.52h35.23c6.27 0 12.13-3.58 14.73-9.29C630.57 210.48 640 170.36 640 128s-9.42-82.48-25.94-118.71zM489.06 64h-33.73c-11.01 0-18.61 10.83-14.86 21.18 4.93 13.58 7.55 27.98 7.55 42.82s-2.62 29.24-7.55 42.82c-3.76 10.35 3.85 21.18 14.86 21.18h33.73c7.02 0 13.46-4.49 15.41-11.24 4.9-16.97 7.53-34.64 7.53-52.76 0-18.12-2.64-35.79-7.54-52.76-1.94-6.75-8.39-11.24-15.4-11.24zm-116.3 100.12c7.05-10.29 11.2-22.71 11.2-36.12 0-35.35-28.63-64-63.96-64-35.32 0-63.96 28.65-63.96 64 0 13.41 4.15 25.83 11.2 36.12l-130.5 313.41c-3.4 8.15.46 17.52 8.61 20.92l29.51 12.31c8.15 3.4 17.52-.46 20.91-8.61L244.96 384h150.07l49.2 118.15c3.4 8.16 12.76 12.01 20.91 8.61l29.51-12.31c8.15-3.4 12-12.77 8.61-20.92l-130.5-313.41zM271.62 320L320 203.81 368.38 320h-96.76z"}}]})(props);
  }

  const AirPlayPanel = ({ serverApi }) => {
      const [serverName, setServerName] = React.useState("");
      const [fps, setFps] = React.useState(60);
      const [avdec, setAvdec] = React.useState(true);
      const [pin, setPin] = React.useState(true);
      const [customArgs, setCustomArgs] = React.useState("");
      const [saved, setSaved] = React.useState(false);
      React.useEffect(() => {
          serverApi.callPluginMethod("get_settings", {}).then((res) => {
              if (res.result) {
                  setServerName(res.result.server_name || "");
                  setFps(res.result.fps || 60);
                  setAvdec(res.result.avdec ?? true);
                  setPin(res.result.pin ?? true);
                  setCustomArgs(res.result.custom_args || "");
              }
          });
          const unregisterMirroring = serverApi.routerHook?.addNotificationListener("screen_mirroring", (data) => {
              serverApi.toaster?.toast({
                  title: `${data.device || "Apple Device"} — Screen Mirroring`,
                  body: "Mirroring session started",
                  duration: 3500,
                  playSound: false,
              });
          });
          const unregisterAudio = serverApi.routerHook?.addNotificationListener("now_playing", (data) => {
              const artist = data.artist || "Unknown Artist";
              const title = data.title || "Unknown Track";
              serverApi.toaster?.toast({
                  title: `${data.device || "Apple Device"} — Now Playing`,
                  body: `${artist} — ${title}`,
                  duration: 4000,
                  playSound: false,
                  icon: data.cover ? (React.createElement("img", { src: data.cover, style: {
                          width: "44px",
                          height: "44px",
                          borderRadius: "6px",
                          objectFit: "cover",
                          marginRight: "6px"
                      } })) : undefined
              });
          });
          return () => {
              if (unregisterMirroring)
                  unregisterMirroring();
              if (unregisterAudio)
                  unregisterAudio();
          };
      }, []);
      const saveSettings = async (overrides = {}) => {
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
      return (React.createElement(ui.PanelSection, { title: "AirPlay Settings" },
          React.createElement(ui.PanelSectionRow, null,
              React.createElement(ui.TextField, { label: "Device Name", value: serverName, onChange: (e) => setServerName(e.target.value) })),
          React.createElement(ui.PanelSectionRow, null,
              React.createElement(ui.DropdownItem, { label: "Frame Rate (FPS)", menuLabel: "FPS", rgOptions: [
                      { data: 60, label: "60 FPS (Smooth)" },
                      { data: 30, label: "30 FPS (Power Saving)" }
                  ], selectedOption: fps, onChange: (newFps) => {
                      setFps(newFps.data);
                      saveSettings({ fps: newFps.data });
                  } })),
          React.createElement(ui.PanelSectionRow, null,
              React.createElement(ui.ToggleField, { label: "Hardware Decoder (-avdec)", description: "GPU/libav accelerated decoding", checked: avdec, onChange: (val) => {
                      setAvdec(val);
                      saveSettings({ avdec: val });
                  } })),
          React.createElement(ui.PanelSectionRow, null,
              React.createElement(ui.ToggleField, { label: "Require PIN (-p)", description: "Enforce one-time pairing code", checked: pin, onChange: (val) => {
                      setPin(val);
                      saveSettings({ pin: val });
                  } })),
          React.createElement(ui.PanelSectionRow, null,
              React.createElement(ui.TextField, { label: "Custom Arguments", description: "Extra UxPlay launch flags", value: customArgs, onChange: (e) => setCustomArgs(e.target.value) })),
          React.createElement(ui.PanelSectionRow, null,
              React.createElement(ui.ButtonItem, { layout: "below", onClick: () => saveSettings() }, saved ? "Saved!" : "Apply Settings"))));
  };
  var index = ui.definePlugin((serverApi) => {
      return {
          title: React.createElement("div", { className: "AirPlayTitle" }, "AirPlay"),
          content: React.createElement(AirPlayPanel, { serverApi: serverApi }),
          icon: React.createElement(FaBroadcastTower, null)
      };
  });

  return index;

})(React, ui);

export default plugin;
