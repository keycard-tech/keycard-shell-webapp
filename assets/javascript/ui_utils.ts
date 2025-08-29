import { CameraDevice } from "html5-qrcode";
import Transport from "@choppu/shelljs/lib/transport";

export namespace UIUtils {
  export function handleUpdateLoadProgress(transport: Transport, loadBar: HTMLProgressElement, progressPercent: HTMLSpanElement, cbFunc: () => void) : void {
    let dataI = 0;

    if (dataI == 0) {
      dataI = 1;
      let pBarProgress = 0;
      transport.on("chunk-loaded", (progress: any) => {
        pBarProgress += progress;
        
        if (pBarProgress >= loadBar.max - progress) {
          transport.off("chunk-loaded", () => {});
          dataI = 0;
          cbFunc();
        } else {
          loadBar.value = pBarProgress;
          progressPercent.innerHTML = `${Math.round((pBarProgress / loadBar.max) * 100)} %`;
        }
      })
    }
  }

  export function handleMessageLog(msgField: HTMLSpanElement, msg: string) : void {
    msgField.innerHTML = msg;
    msgField.classList.contains("keycard_shell__display-none") && msg != "" ? msgField.classList.remove("keycard_shell__display-none") : msgField.classList.add("keycard_shell__display-none");
  }

  export function addCameraSelectOption(selectField: HTMLSelectElement, options: CameraDevice[]) : void {
    for(let i = 0; i < options.sort().length; i++) {
      let option = new Option(options[i].label,options[i].id);
      selectField.add(option, undefined);
    }
  }

  export function createElement(type: string, id: string, styleClass: string, parentContainer: HTMLElement, content?: string) : HTMLElement {
    const childContainer = document.createElement(type);
    childContainer.classList.add(styleClass);
    childContainer.id = id;
    childContainer.innerHTML = content ? content : null;

    parentContainer.append(childContainer);

    return childContainer;
  }

  export function shortLink(link: string, maxChars: number) : string {
    return link.length <= maxChars ? link.substring(0, maxChars) : link.substring(0, maxChars) + "...";
  }

  export function parseFWVersion(version: string) : number {
    let verArr = Array.from(version.split('.'), Number);
    return (verArr[0] * 1000000) + (verArr[1] * 1000) + verArr[2];
  }

  export function getOS() : string {
    if(navigator.userAgent.includes('Mac')) {
        return 'mac';
    } else if(navigator.userAgent.includes('Windows')) {
        return 'windows';
    } else if(navigator.userAgent.includes('Linux')) {
        return 'linux';
    } else {
        return '';
    }
  }
}