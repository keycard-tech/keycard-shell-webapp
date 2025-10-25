import { Html5Qrcode } from "html5-qrcode";
import { UIUtils } from "./ui_utils";
import { URDecoder } from "@ngraveio/bc-ur";
import { QRUtils } from "./qr_utils";

const verState = {
  1: "dev_auth_init",
  2: "dev_auth_device",
  3: "dev_auth_server"
};

export namespace VerifyUtils {
    export async function verify(data: FormData, csrftoken: string, url: string) : Promise<any|void> {
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

    export function handleDeviceResponse(resp: Buffer, challenge: Uint8Array) : FormData {
        const reqData = new FormData();
        const deviceId = (resp[2] as any).toString("hex");
        const deviceChallenge = (resp[6] as any).toString("hex");
        const signature = (resp[7] as any).toString("hex");

        reqData.append("device_id", deviceId);
        reqData.append("challenge", deviceChallenge);
        reqData.append("signature", signature);
        reqData.append("initial_challenge", Buffer.from(challenge).toString("hex"));

        return reqData;
    } 

    export async function videoPermissionsGranted() : Promise<boolean> {
        return (await navigator.permissions.query({name: 'camera'})).state == "granted";
    }
    
    export async function handleCamerasSelector(cameraSelector: HTMLSelectElement) : Promise<string> {
        return await Html5Qrcode.getCameras().then((devices) => {
            UIUtils.addCameraSelectOption(cameraSelector, devices);
            return cameraSelector.value;
        });
    }

    export async function stopScanning(html5QrCode:Html5Qrcode) : Promise<void> {
        if (html5QrCode.isScanning) {
            await html5QrCode.stop();
            html5QrCode.clear();
        }
    }

    export async function onScanSuccess(decodedText: any, challenge: Uint8Array, decoder: URDecoder, csrftoken: string, html5QrCode: Html5Qrcode, postReqURL: string, onSuccessFunc: (r: any) => void, onErrorFunc: (err?: boolean) => void) : Promise<void> {
        await stopScanning(html5QrCode);

    try {
        const data = QRUtils.decodeQR(decoder, decodedText);
        const status = data[1];
    
        if (verState[status as keyof typeof verState] == "dev_auth_device") {
            const reqData = handleDeviceResponse(data, challenge);
            const r = await verify(reqData, csrftoken, postReqURL) as any;
            onSuccessFunc(r);
        } else {
            onErrorFunc();
        }
    } catch(e) {
        onErrorFunc(true);
    }
}

    export function onScanFailure(error: any) : void {
        return error;
    }

    export async function startScanning(challenge: Uint8Array, decoder: URDecoder, csrftoken: string, html5QrCode: Html5Qrcode, cameraId: string, postReqURL: string, onSuccessFunc: (r: any) => void, onErrorFunc: (err: boolean) => void) : Promise<void> {
        const config = {fps: 10, qrbox: 600, aspectRatio: 1};
    
        html5QrCode.start(
          { facingMode: { exact: "environment"} },
          config,
          async (decodedText) => await onScanSuccess(decodedText, challenge, decoder, csrftoken, html5QrCode, postReqURL, onSuccessFunc, onErrorFunc),
          (errorMessage) => onScanFailure(errorMessage)
        )
        .catch((err) => {
          html5QrCode.start(
          cameraId,
          config,
          async (decodedText) => await onScanSuccess(decodedText, challenge, decoder, csrftoken, html5QrCode, postReqURL, onSuccessFunc, onErrorFunc),
          (errorMessage) => onScanFailure(errorMessage)
        )});
    }
}