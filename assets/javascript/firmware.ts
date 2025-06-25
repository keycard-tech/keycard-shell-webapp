import KProJS from "kprojs";
import TransportWebHID from "kprojs-web-hid";
import Eth from "kprojs/lib/eth";
import Transport, { StatusCodes } from "kprojs/lib/transport";
import { marked } from 'marked';
import { UIUtils } from "./ui_utils";

if (!('process' in window)) {
  // @ts-ignore
  window.process = {}
}

async function handleFirmwareUpdate() : Promise<void> {
  const updateFirmwareBtn = document.getElementById("btn-fw-update") as HTMLButtonElement;
  const progressBar = document.getElementById("fw-progress");
  const fwLoad = document.getElementById("progress-bar") as HTMLProgressElement;
  const mediaPrefixField = document.getElementById("media-prefix") as HTMLInputElement;
  const mediaPrefix = mediaPrefixField.value;
  const fwChangelogLabel = document.getElementById("release-note-fw-version") as HTMLElement;
  const fwChangelogText = document.getElementById("release-note-fw-changelog") as HTMLDivElement;
  const readMoreBtn = document.getElementById("release-note-read-more-btn") as HTMLButtonElement;
  const readMoreIc = document.getElementById("release-note-read-more-btn-ic") as HTMLSpanElement;
  const releaseNotesContainer = document.getElementById("release-note-container") as HTMLDivElement;
  const logMessage = document.getElementById("kpro-web-msg") as HTMLSpanElement;

  UIUtils.handleMessageLog(logMessage, "");

  const context = await fetch("./context").then((r) => r.json());

  const fw = await fetch(mediaPrefix + context["fw_path"]).then((r) => r.arrayBuffer());
  const changelog = await fetch(mediaPrefix + context["changelog_path"]).then((r) => r.text());

  fwLoad.max = fw.byteLength;

  fwChangelogLabel.innerHTML = "Version " + context["version"];
  fwChangelogText.innerHTML = marked.parse(changelog);

  let transport: Transport;
  let appEth: Eth;

  updateFirmwareBtn.addEventListener("click", async () => {
    try {
      transport = await TransportWebHID.create();
      appEth = new KProJS.Eth(transport);
      let { fwVersion } = await appEth.getAppConfiguration();

      if (fwVersion == context["version"]) {
        UIUtils.handleMessageLog(logMessage, "You already have the latest version of the firmware");
      } else {
        progressBar.classList.remove("keycard_shell__display-none");
        UIUtils.handleFWLoadProgress(transport, fwLoad);

        await appEth.loadFirmware(fw);
        await transport.close();

        progressBar.classList.add("keycard_shell__display-none");
        UIUtils.handleMessageLog(logMessage, "Keycard Pro updated successfully");
      }
    } catch (e) {
      if (e instanceof KProJS.KProError.TransportOpenUserCancelled) {
        UIUtils.handleMessageLog(logMessage, "Error connecting to device. Check if Keycard Pro is connected");
      } else {
        let m = (e.statusCode == StatusCodes.SECURITY_STATUS_NOT_SATISFIED) ? "Firmware update canceled by user" :  "Error: Invalid data. Failed to update the firmware";
        UIUtils.handleMessageLog(logMessage, m);
      }
      progressBar.classList.add("keycard_shell__display-none");
    }
  });

  readMoreBtn.addEventListener("click", () => {
    if(releaseNotesContainer.offsetHeight == 360) {
      releaseNotesContainer.style.height = "auto";
      releaseNotesContainer.style.transitionProperty = "height";
      releaseNotesContainer.style.transitionTimingFunction ="ease-in";
      releaseNotesContainer.style.transitionDelay = ".5s";
      readMoreIc.innerHTML = "keyboard_double_arrow_up";
    } else {
      releaseNotesContainer.style.height = "360px";
      readMoreIc.innerHTML = "keyboard_double_arrow_down";
    }
  });
}

handleFirmwareUpdate();