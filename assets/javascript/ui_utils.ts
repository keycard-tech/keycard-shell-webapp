import Transport from "kprojs/lib/transport";

export namespace UIUtils {
  export function handleUpdateLoadProgress(transport: Transport, loadBar: HTMLProgressElement, progressPercent: HTMLSpanElement) : void {
    let dataI = 0;

    if (dataI == 0) {
      dataI = 1;
      let pBarProgress = 0;
      transport.on("chunk-loaded", (progress: any) => {
        if (progress >= loadBar.max) {
          transport.off("chunk-loaded", () => {});
          dataI = 0;
        } else {
          pBarProgress += progress;
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

  export function addSelectOption(selectField: HTMLSelectElement, options: string[]) : void {
    for(let i = 0; i < options.sort().length; i++) {
      let option = new Option(options[i],options[i]);
      selectField.add(option, undefined);
    }
  }
}