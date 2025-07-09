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

const mediaPrefix = document.getElementById('db_updater__media-prefix') as HTMLInputElement;
const dbUSBUpdateBtn = document.getElementById("btn-db-usb-update") as HTMLButtonElement;
const logMessage = document.getElementById("kpro-db-web-msg") as HTMLSpanElement;
const dbLoad = document.getElementById("db-progress-bar") as HTMLProgressElement;
const versionSelect = document.getElementById("db-current-version") as HTMLSelectElement;
const dbQR = new QRious({element: document.querySelector('canvas')}) as any;
const dbQRContainer = document.getElementById("qr-container") as HTMLDivElement;
const backBtn = document.getElementById("back-btn") as HTMLAnchorElement;
const backBtnContainer = document.getElementById("back-btn-container") as HTMLDivElement;

const startQRUpdateBtn = document.getElementById("erc20db-qr-update-btn") as HTMLButtonElement;
const startUsbUpdateBtn = document.getElementById("erc20db-usb-update-btn") as HTMLButtonElement;
const startUpdateScreen = document.getElementById("start-db-update-screen") as HTMLDivElement;
const startQRUpdateScreen = document.getElementById("start-db-qr-update-screen") as HTMLDivElement;
const startUsbUpdateScreen = document.getElementById("start-db-usb-update-screen") as HTMLDivElement;
const usbUpdateVersionScreen = document.getElementById("db-usb-update-version-screen") as HTMLDivElement;
const usbDBUpdatingScreen = document.getElementById("db-usb-update-in-progress-screen") as HTMLDivElement;
const usbUpdateSuccessScreen = document.getElementById("db-usb-update-success-screen") as HTMLDivElement;
const usbUpdateFailedScreen = document.getElementById("db-usb-update-failed-screen") as HTMLDivElement;
  
const displayNoneClass = "keycard_shell__display-none";

const pageHeading = document.getElementById("db-page-heading") as HTMLHeadElement;
const pagePrompt = document.getElementById("db-page-prompt") as HTMLSpanElement;

const updateSuccessMessage = document.getElementById("db-update-finished-success-message") as HTMLSpanElement;
const updateErrorMessage = document.getElementById("db-update-finished-err-message") as HTMLSpanElement;
const updatedDBVersion = document.getElementById("db-updated-version") as HTMLSpanElement;

const maxFrLength = 400;

const latestDBVersion = document.getElementById("latest-db-version") as HTMLSpanElement;
const erc20dbVersionProgress = document.getElementById("update-progress-db-version") as HTMLSpanElement;

async function generateQR(context: any, mediaPrefix: string, currentVersion: string, maxFragmentLength: number, dbQR: any) : Promise<UREncoder> {
  const resp = await fetch(mediaPrefix + context["version"] + '/deltas/delta-' + context["version"] + '-' + currentVersion + '.bin');
  const deltaArr = await resp.arrayBuffer();
  const deltaBuff = QRUtils.toBuffer(deltaArr);
  const ur = new UR(deltaBuff, "fs-data");

  return new UREncoder(ur, maxFragmentLength);
}

function renderStartScreen(activeStep: HTMLDivElement) : void {
    if(activeStep) {
        pageHeading.innerHTML = TextStr.UpdateStartHeading;
        pagePrompt.innerHTML = TextStr.updateStartPrompt;
        activeStep.classList.add(displayNoneClass);
        activeStep.classList.remove("keycard_shell__active-step");
        backBtnContainer.classList.add(displayNoneClass);
        startUpdateScreen.classList.remove(displayNoneClass);
    }
}

function renderNextScreeen(currentScreen: HTMLDivElement, nextScreen: HTMLDivElement, backBtn?: boolean) : void {
    currentScreen.classList.add(displayNoneClass);

    if(currentScreen.classList.contains("keycard_shell__active-step")) {
        currentScreen.classList.remove("keycard_shell__active-step");
    }
    
    nextScreen.classList.remove(displayNoneClass);
    nextScreen.classList.add("keycard_shell__active-step");
    
    if(backBtn) {
        backBtnContainer.classList.remove(displayNoneClass);
    }   
}

async function handleERC20DB() : Promise<void> {
  const context = await fetch("./context").then((r: any) => r.json());
  const resp = await fetch(mediaPrefix.value + context["db_path"]);
  const dbArr = await resp.arrayBuffer();

  UIUtils.addSelectOption(versionSelect, context["available_db_versions"]);

  let transport: Transport;
  let appEth: Eth;

  let encoder: {enc: UREncoder | undefined} = {enc: undefined};

  dbLoad.max = dbArr.byteLength;

  latestDBVersion.innerHTML = context["version"];
  erc20dbVersionProgress.innerHTML = `${TextStr.progressVersionPrompt} ${context["version"]}`

  startQRUpdateBtn.addEventListener("click", () => {
    pageHeading.innerHTML = TextStr.QRUpdateHeading;
    pagePrompt.innerHTML = TextStr.QrUpdatePrompt;
    renderNextScreeen(startUpdateScreen, startQRUpdateScreen, true);
  });

  versionSelect.addEventListener("change", async() => {
    if(versionSelect.value != "") {
      encoder.enc = await generateQR(context, mediaPrefix.value, versionSelect.value, maxFrLength, dbQR);
      dbQRContainer.classList.remove("keycard_shell__display-none");
    } else {
      dbQRContainer.classList.add("keycard_shell__display-none");
    }
  });

  setTimeout(() => {QRUtils.generateQRPart(encoder, dbQR, true, 450)}, 500);

  startUsbUpdateBtn.addEventListener("click", async () => {
    if(appEth) {
        pagePrompt.innerHTML = TextStr.shellConnectedPrompt; 
        renderNextScreeen(startUpdateScreen, usbUpdateVersionScreen, true);
    } else {
        pageHeading.innerHTML = TextStr.UsbUpdateHeading;
        pagePrompt.innerHTML = "";
        renderNextScreeen(startUpdateScreen, startUsbUpdateScreen, true);
        
        try {
            transport = await TransportWebHID.create();
            appEth = new KProJS.Eth(transport);

            transport.on("disconnect", async () => {
                const activeStep = document.getElementsByClassName("keycard_shell__active-step")[0] as HTMLDivElement;

                await transport.close();
                transport = null;
                appEth = null;
                
                updateErrorMessage.innerHTML = "Error connecting to device";
                renderNextScreeen(activeStep, usbUpdateFailedScreen);
            });

            renderNextScreeen(startUsbUpdateScreen, usbUpdateVersionScreen, false);
            pagePrompt.innerHTML = TextStr.shellConnectedPrompt;
        } catch(err) {
            renderStartScreen(startUsbUpdateScreen);
        }
    }
  });

  dbUSBUpdateBtn.addEventListener("click", async () => {
    updatedDBVersion.innerHTML = `Version ${context["version"]}`;
    try {
        let { erc20Version } = await appEth.getAppConfiguration();

      if (erc20Version == context["version"]) {
        updateSuccessMessage.innerHTML = "Database already up to date";
        renderNextScreeen(usbUpdateVersionScreen, usbUpdateSuccessScreen, false);
        pagePrompt.innerHTML = TextStr.shellDisconnectPrompt;
        backBtnContainer.classList.add(displayNoneClass);
      } else {
        renderNextScreeen(usbUpdateVersionScreen, usbDBUpdatingScreen, false);
        backBtnContainer.classList.add(displayNoneClass);
        UIUtils.handleFWLoadProgress(transport, dbLoad);

        await appEth.loadERC20DB(dbArr);
        await transport.close();

        updateSuccessMessage.innerHTML = "Database updated";
        renderNextScreeen(usbDBUpdatingScreen, usbUpdateSuccessScreen);
        pagePrompt.innerHTML = TextStr.shellDisconnectPrompt;
      }
    } catch (e) {
        pagePrompt.innerHTML = "";
        const activeStep = document.getElementsByClassName("keycard_shell__active-step")[0] as HTMLDivElement;
        if (e instanceof KProJS.KProError.TransportOpenUserCancelled) {
            updateErrorMessage.innerHTML = "Error connecting to device";
            renderNextScreeen(activeStep, usbUpdateFailedScreen);
        } else {
            updateErrorMessage.innerHTML = (e.statusCode == StatusCodes.SECURITY_STATUS_NOT_SATISFIED) ? "Database update canceled by user" :  "Database transfer failed";
            renderNextScreeen(activeStep, usbUpdateFailedScreen);
        }
      
      backBtnContainer.classList.add(displayNoneClass);
      await transport.close();
    }
  });

  backBtn.addEventListener("click", (e) => {
    const activeStep = document.getElementsByClassName("keycard_shell__active-step")[0] as HTMLDivElement;
    renderStartScreen(activeStep);
    e.preventDefault();
  });
}

handleERC20DB();
