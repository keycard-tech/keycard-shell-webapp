import { QRUtils } from "./qr_utils";
import {UR, UREncoder, URDecoder} from '@ngraveio/bc-ur'
import {Html5Qrcode} from "html5-qrcode";

const QRious = require('qrious');
const postReqURL = './verify';
const verState = {
  1: "dev_auth_init",
  2: "dev_auth_device",
  3: "dev_auth_server"
};
const keys = {
  1: "dev_auth_device",
  2: "device_id",
  3: "first_auth",
  4: "auth_time",
  5: "auth_count",
  6: "challenge",
  7: "signature",
  8: "initial_challenge"
};
const maxFragmentLength = 500;

const step1Container = document.getElementById("kpro_web__verify-step1");
const step2Container = document.getElementById("kpro_web__verify-step2");
const step3Container = document.getElementById("kpro_web__verify-step3");
const step4Container = document.getElementById("kpro_web__verify-step4");
const stepPrompt = document.getElementById("keycard_shell__verify-step-prompt") as HTMLParagraphElement;
const deviceSuccessQRContainer = document.getElementById("verify-success-qr-container") as HTMLDivElement;
const verifyResultHeader = document.getElementById("verify-result-header") as HTMLHeadingElement;
const verifyResultPrompt = document.getElementById("verify-result-prompt") as HTMLParagraphElement;
const scanFinishedButtonLink = document.getElementById("device_verify__scan-finished-link") as HTMLLinkElement;
const scanFinishedButton = document.getElementById("device_verify__scan-finished") as HTMLInputElement;
const scanVerificationCountWarning = document.getElementById("device-verification-count-warning") as HTMLDivElement;
const dbUpdateVersion = document.getElementById("db-update-version") as HTMLSpanElement;
const fwUpdateVersion = document.getElementById("fw-update-version") as HTMLSpanElement;
const bottomHeading = document.getElementById("bottom-heading") as HTMLDivElement;
const updateDB = document.getElementById("update-db") as HTMLDivElement;
const updateFW = document.getElementById("update-fw") as HTMLDivElement;
const bottomContainer = document.getElementById("bottom-content-container") as HTMLDivElement;

async function verify(data: FormData, csrftoken: string, url: string) : Promise<any|void> {
  try {
    return await fetch(url, {
      method: 'POST',
      headers: {'X-CSRFToken': csrftoken},
      body: data,
      mode: 'same-origin'
    }).then(async (data) => {
      return await data.json();
    });
  } catch(err) {
    console.log(err);
  }
}

async function stopScanning(html5QrCode:Html5Qrcode) : Promise<void> {
  if (html5QrCode.isScanning) {
    await html5QrCode.stop();
    html5QrCode.clear();
  }
}

function handleDeviceResponse(resp: Buffer, challenge: Uint8Array) : FormData {
  const reqData = new FormData();
  const deviceId = (resp[2] as any).toString("hex");
  const deviceChallenge = (resp[6] as any).toString("hex");
  const signature = (resp[7] as any).toString("hex");

  reqData.append(keys[2], deviceId);
  reqData.append(keys[6], deviceChallenge);
  reqData.append(keys[7], signature);
  reqData.append(keys[8], Buffer.from(challenge).toString("hex"));

  return reqData;
}

function handleVerificationComplete(r: any) : void {
  step3Container.classList.add('keycard_shell__display-none');
  step4Container.classList.remove('keycard_shell__display-none');
  bottomHeading.classList.remove('keycard_shell__display-none');
  updateDB.classList.remove('keycard_shell__display-none');
  updateFW.classList.remove('keycard_shell__display-none');

  if(window.innerWidth < 700) {
    bottomContainer.style.flexDirection = "column-reverse";
  } else {
    bottomContainer.style.flexDirection = "row-reverse";
  }

  if(r['status'] == 'success') {
    const successQR = new QRious({element: document.getElementById('device_success__qr')}) as any;
    const ur = new UR(Buffer.from(r.payload, "hex"), "dev-auth");
    const encoder = {enc: new UREncoder(ur, maxFragmentLength)};

    QRUtils.generateQRPart(encoder, successQR, false, 400);
    deviceSuccessQRContainer.classList.remove('keycard_shell__display-none');

    verifyResultHeader.innerText = "Your Shell is authentic";
    verifyResultPrompt.innerHTML = "Scan the QR code with your Shell to verify the site hasn't been compromised by malicious extensions or viruses.";
    scanFinishedButtonLink.href = "https://keycard.tech/keycard";

    if(r['counter'] > 1) {
        scanVerificationCountWarning.classList.remove('keycard_shell__display-none');
    } 
  } else {
    handleQRErrorUI();
  }
}

function handleQRErrorUI(qrError?: boolean) : void {
    step3Container.classList.add('keycard_shell__display-none');
    step4Container.classList.remove('keycard_shell__display-none');
    verifyResultHeader.innerText = qrError ? "Shell was not verified" : "Your Shell is not authentic";
    verifyResultPrompt.innerHTML = qrError ? "Something went wrong. Go to Settings/Device/ Verification on your Shell and try again." : "Check Keycard Shell documentation for more details or contact us.";
    scanFinishedButton.value = qrError ? "Try again" : "Learn more";
    if(qrError) {
        scanFinishedButtonLink.addEventListener("click", (e) => {
            location.reload();
            e.preventDefault();
        });
    } else {
        scanFinishedButtonLink.href = "https://keycard.tech/docs/overview";
    }
    
}

async function onScanSuccess(decodedText: any, challenge: Uint8Array, decoder: URDecoder, csrftoken: string, html5QrCode: Html5Qrcode) : Promise<void> {
    await stopScanning(html5QrCode);

    try {
        const data = QRUtils.decodeQR(decoder, decodedText);
        const status = data[1];
    
        if (verState[status as keyof typeof verState] == "dev_auth_device") {
            const reqData = handleDeviceResponse(data, challenge);
            const r = await verify(reqData, csrftoken, postReqURL) as any;
            handleVerificationComplete(r);
        } else {
            handleQRErrorUI();
        }
    } catch(e) {
        handleQRErrorUI(true);
    }
}

function onScanFailure(error: any) : void {
  return error;
}

async function videoPermissionsGranted() : Promise<boolean> {
    return (await navigator.permissions.query({name: 'camera'})).state == "granted";
}

async function startScanning(challenge: Uint8Array, decoder: URDecoder, csrftoken: string) : Promise<void> {
    step3Container.classList.remove('keycard_shell__display-none');

    const html5QrCode = new Html5Qrcode("device_verify__qr-reader");
    const config = {fps: 10, qrbox: 600, aspectRatio: 1};

    const cameraId = await Html5Qrcode.getCameras().then(devices => {
        if (devices && devices.length) {
        return devices[0].id;
        }
    });

    html5QrCode.start(
      { facingMode: { exact: "environment"} },
      config,
      async (decodedText) => await onScanSuccess(decodedText, challenge, decoder, csrftoken, html5QrCode),
      (errorMessage) => onScanFailure(errorMessage)
    )
    .catch((err) => {
      html5QrCode.start(
      cameraId,
      config,
      async (decodedText) => await onScanSuccess(decodedText, challenge, decoder, csrftoken, html5QrCode),
      (errorMessage) => onScanFailure(errorMessage)
    )});
}

async function handleVerifyDevice() : Promise<void> {
  const csrftoken = document.getElementById('device_verify__csfr') as HTMLInputElement;
  const next_btn = document.getElementById("device_verify__next-button");
  const scan_btn = document.getElementById("device_verify__scan-button");
  const verifyQR = new QRious({element: document.getElementById('device_verify__qr')}) as any;

  const challenge = crypto.getRandomValues(new Uint8Array(32));

  const payload = QRUtils.encodeChallenge(challenge);
  const ur = new UR(payload, "dev-auth");
  const encoder = {enc: new UREncoder(ur, maxFragmentLength)};
  const decoder = new URDecoder();
  QRUtils.generateQRPart(encoder, verifyQR, false, 400);

  const ercDBContext = await fetch("../context").then((r: any) => r.json());
  const fwContext = await fetch("../firmware/context").then((r) => r.json());
  dbUpdateVersion.innerHTML = ercDBContext["version"];
  fwUpdateVersion.innerHTML = fwContext["version"];

  next_btn.addEventListener("click", async () => {
    if (step2Container.classList.contains('keycard_shell__display-none')) {
        if(await videoPermissionsGranted()) {
            step1Container.classList.add('keycard_shell__display-none');
            startScanning(challenge, decoder, csrftoken.value);
        } else {
            step1Container.classList.add('keycard_shell__display-none');
            step2Container.classList.remove('keycard_shell__display-none');
            stepPrompt.innerHTML = `Go to Settings / Device / Verification on your Shell and scan this QR to initiate the device verification.<br>`;    
        }
    }
  });

  scan_btn.addEventListener("click", async () => {
    step2Container.classList.add('keycard_shell__display-none');
    startScanning(challenge, decoder, csrftoken.value);
  });
}

handleVerifyDevice();