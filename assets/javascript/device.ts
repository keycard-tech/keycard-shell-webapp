import { QRUtils } from "./qr_utils";
import { TextStr } from "./text_str";
import {UR, UREncoder, URDecoder} from '@ngraveio/bc-ur'
import {Html5Qrcode} from "html5-qrcode";
import { VerifyUtils } from "./verify_utils";

const QRious = require('qrious');
const postReqURL = './verify';

const maxFragmentLength = 500;

const step1Container = document.getElementById("kpro_web__verify-step1");
const step2Container = document.getElementById("kpro_web__verify-step2");
const step3Container = document.getElementById("kpro_web__verify-step3");
const step4Container = document.getElementById("kpro_web__verify-step4");
const stepPrompt = document.getElementById("page-top-text") as HTMLParagraphElement;
const deviceSuccessQRContainer = document.getElementById("verify-success-qr-container") as HTMLDivElement;
const verifyResultHeading = document.getElementById("verify-result-heading") as HTMLHeadingElement;
const verifyResultPrompt = document.getElementById("verify-result-prompt") as HTMLParagraphElement;
const scanFinishedButtonLink = document.getElementById("device_verify__scan-finished-link") as HTMLLinkElement;
const scanFinishedButton = document.getElementById("device_verify__scan-finished") as HTMLInputElement;
const scanVerificationCountWarning = document.getElementById("device-verification-count-warning") as HTMLDivElement;

const bc = new BroadcastChannel('process_channel');

function handleVerificationComplete(r: any) : void { 
  bc.postMessage({state: 'success', process: 'verify'});
  step3Container.classList.add('keycard_shell__display-none');
  step4Container.classList.remove('keycard_shell__display-none');

  if(r['status'] == 'success') {
    const successQR = new QRious({element: document.getElementById('device_success__qr')}) as any;
    const ur = new UR(Buffer.from(r.payload, "hex"), "dev-auth");
    const encoder = {enc: new UREncoder(ur, maxFragmentLength)};

    QRUtils.generateQRPart(encoder, successQR, false, 400);
    deviceSuccessQRContainer.classList.remove('keycard_shell__display-none');

    verifyResultHeading.innerText = TextStr.verifyAuthenticHeading;
    verifyResultPrompt.innerHTML = TextStr.verifySuccessPrompt;
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
    verifyResultHeading.innerText = qrError ? TextStr.verifyErrorHeading : TextStr.verifyNotAuthenticHeading;
    verifyResultPrompt.innerHTML = qrError ? TextStr.verifyErrorPrompt: TextStr.verifyFailPrompt;
    scanFinishedButton.value = qrError ? TextStr.btnTryAgain : TextStr.btnLearnMore;
    if(qrError) {
        scanFinishedButtonLink.addEventListener("click", (e) => {
            location.reload();
            e.preventDefault();
        });
    } else {
        scanFinishedButtonLink.href = "https://keycard.tech/docs/overview";
    }
    
}

async function handleStartScanning(challenge: Uint8Array, decoder: URDecoder, csrftoken: string, html5QrCode: Html5Qrcode, cameraId: string, zoomContainer: HTMLDivElement) : Promise<void> {
    step3Container.classList.remove('keycard_shell__display-none');
    return await VerifyUtils.startScanning(challenge, decoder, csrftoken, html5QrCode, cameraId, postReqURL, handleVerificationComplete, handleQRErrorUI, zoomContainer);  
}

async function handleVerifyDevice() : Promise<void> {
  const csrftoken = document.getElementById('device_verify__csfr') as HTMLInputElement;
  const next_btn = document.getElementById("device_verify__next-button");
  const scan_btn = document.getElementById("device_verify__scan-button");
  const verifyQR = new QRious({element: document.getElementById('device_verify__qr')}) as any;
  const html5QrCode = new Html5Qrcode("device_verify__qr-reader");

  let cameraId: string;

  const cameraSelector = document.getElementById("camera-selector") as HTMLSelectElement;
  const cameraZoomContainer = document.getElementById("camera-zoom-container") as HTMLDivElement;

  const challenge = crypto.getRandomValues(new Uint8Array(32));

  const payload = QRUtils.encodeChallenge(challenge);
  const ur = new UR(payload, "dev-auth");
  const encoder = {enc: new UREncoder(ur, maxFragmentLength)};
  const decoder = new URDecoder();
  QRUtils.generateQRPart(encoder, verifyQR, false, 400);

  cameraSelector.addEventListener("change", async () => {
    cameraId = cameraSelector.value;
    await VerifyUtils.stopScanning(html5QrCode);
    handleStartScanning(challenge, decoder, csrftoken.value, html5QrCode, cameraId, cameraZoomContainer);
  });

  next_btn.addEventListener("click", async () => {
    if (step2Container.classList.contains('keycard_shell__display-none')) {
        if(await VerifyUtils.videoPermissionsGranted()) {
            cameraId = await VerifyUtils.handleCamerasSelector(cameraSelector);
            step1Container.classList.add('keycard_shell__display-none');
            handleStartScanning(challenge, decoder, csrftoken.value, html5QrCode, cameraId, cameraZoomContainer);
        } else {
            step1Container.classList.add('keycard_shell__display-none');
            step2Container.classList.remove('keycard_shell__display-none');
            stepPrompt.innerHTML = TextStr.stepPrompt;    
        }
    }
  });

  scan_btn.addEventListener("click", async () => {
    cameraId = await VerifyUtils.handleCamerasSelector(cameraSelector);
    step2Container.classList.add('keycard_shell__display-none');
    handleStartScanning(challenge, decoder, csrftoken.value, html5QrCode, cameraId, cameraZoomContainer);
  });
}

handleVerifyDevice();