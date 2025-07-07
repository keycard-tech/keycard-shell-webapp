import {UR, UREncoder} from '@ngraveio/bc-ur'
import { QRUtils } from "./qr_utils";
import KProJS from "kprojs";
import TransportWebHID from "kprojs-web-hid";
import Transport, { StatusCodes } from 'kprojs/lib/transport';
import Eth from 'kprojs/lib/eth';
import { UIUtils } from './ui_utils';
import { TextStr } from './text_str';

const QRious = require('qrious');

if (!('process' in window)) {
  // @ts-ignore
  window.process = {}
}

async function generateQR(context: any, mediaPrefix: string, currentVersion: string, maxFragmentLength: number, dbQR: any) : Promise<UREncoder> {
  const resp = await fetch(mediaPrefix + context["version"] + '/deltas/delta-' + context["version"] + '-' + currentVersion + '.bin');
  const deltaArr = await resp.arrayBuffer();
  const deltaBuff = QRUtils.toBuffer(deltaArr);
  const ur = new UR(deltaBuff, "fs-data");

  return new UREncoder(ur, maxFragmentLength);
}

async function handleERC20DB() : Promise<void> {
  const mediaPrefix = document.getElementById('db_updater__media-prefix') as HTMLInputElement;
  const dbUSBUpdateBtn = document.getElementById("btn-db-usb-update") as HTMLButtonElement;
  const progressBar = document.getElementById("db-progress");
  const logMessage = document.getElementById("kpro-db-web-msg") as HTMLSpanElement;
  const dbLoad = document.getElementById("db-progress-bar") as HTMLProgressElement;
  const versionSelect = document.getElementById("db-current-version") as HTMLSelectElement;
  const dbQR = new QRious({element: document.querySelector('canvas')}) as any;
  const dbQRContainer = document.getElementById("qr-container") as HTMLDivElement;
  const backBtn = document.getElementById("back-btn");
  const backBtnContainer = document.getElementById("back-btn-container");

  const context = await fetch("./context").then((r: any) => r.json());
  const resp = await fetch(mediaPrefix.value + context["db_path"]);
  const dbArr = await resp.arrayBuffer();

  const startDBQRUpdateBtn = document.getElementById("erc20db-qr-update-btn") as HTMLButtonElement;
  const startDBUpdateScreen = document.getElementById("start-db-update-screen") as HTMLDivElement;
  const startDBQRUpdateScreen = document.getElementById("start-db-qr-update-screen") as HTMLDivElement;

  const displayNoneClass = "keycard_shell__display-none";

  const pageHeading = document.getElementById("db-page-heading") as HTMLHeadElement;
  const pagePrompt = document.getElementById("db-page-prompt") as HTMLSpanElement;

  const maxFrLength = 400;

  UIUtils.addSelectOption(versionSelect, context["available_db_versions"]);

  let transport: Transport;
  let appEth: Eth;

  let encoder: {enc: UREncoder | undefined} = {enc: undefined};

  //dbLoad.max = dbArr.byteLength;

  startDBQRUpdateBtn.addEventListener("click", (e) => {
    pageHeading.innerHTML = TextStr.QRUpdateHeading;
    pagePrompt.innerHTML = TextStr.QrUpdatePrompt;
    startDBUpdateScreen.classList.add(displayNoneClass);
    startDBQRUpdateScreen.classList.remove(displayNoneClass);
    startDBQRUpdateScreen.classList.add("keycard_shell__active-step");
    backBtnContainer.classList.remove(displayNoneClass);
    e.preventDefault();
  });

  backBtn.addEventListener("click", (e) => {
    const activeStep = document.getElementsByClassName("keycard_shell__active-step")[0];

    if(activeStep) {
        activeStep.classList.add(displayNoneClass);
        activeStep.classList.remove("keycard_shell__active-step");
        backBtnContainer.classList.add(displayNoneClass);
        startDBUpdateScreen.classList.remove(displayNoneClass);
    }
    e.preventDefault();
  })

  versionSelect.addEventListener("change", async() => {
    if(versionSelect.value != "") {
      encoder.enc = await generateQR(context, mediaPrefix.value, versionSelect.value, maxFrLength, dbQR);
      dbQRContainer.classList.remove("keycard_shell__display-none");
    } else {
      dbQRContainer.classList.add("keycard_shell__display-none");
    }
  });

  setTimeout(() => {QRUtils.generateQRPart(encoder, dbQR, true, 450)}, 500);

  /* dbUSBUpdateBtn.addEventListener("click", async () => {
    try {
      transport = await TransportWebHID.create();
      appEth = new KProJS.Eth(transport);
      let { erc20Version } = await appEth.getAppConfiguration();

      if (erc20Version == context["version"]) {
        UIUtils.handleMessageLog(logMessage, "You already have the latest ERC20 database version");
      } else {
        progressBar.classList.remove("keycard_shell__display-none");
        UIUtils.handleFWLoadProgress(transport, dbLoad);

        await appEth.loadERC20DB(dbArr);
        await transport.close();

        progressBar.classList.add("keycard_shell__display-none");
        UIUtils.handleMessageLog(logMessage, "ERC20 database updated successfully");
      }
    } catch (e) {
      if (e instanceof KProJS.KProError.TransportOpenUserCancelled) {
        UIUtils.handleMessageLog(logMessage, "Error connecting to device. Check if Keycard Pro is connected");
      } else {
       let m = (e.statusCode == StatusCodes.SECURITY_STATUS_NOT_SATISFIED) ? "ERC20 database update canceled by user" :  "Error: Invalid data. Failed to update the ERC20 database";
       UIUtils.handleMessageLog(logMessage, m)
      }
      progressBar.classList.add("keycard_shell__display-none");
    }
  }); */
}

handleERC20DB();
