import Transport from "kprojs/lib/transport";

export namespace UIUtils {
  export function handleFWLoadProgress(transport: Transport, loadBar: HTMLProgressElement) : void {
    let fwI = 0;

    if (fwI == 0) {
      fwI = 1;
      let pBarProgress = 0;
      transport.on("chunk-loaded", (progress: any) => {
        if (progress >= loadBar.max) {
          transport.off("chunk-loaded", () => {});
          fwI = 0;
        } else {
          pBarProgress += progress
          loadBar.value = pBarProgress;
        }
      })
    }
  }

  export function handleMessageLog(msgField: HTMLSpanElement, msg: string) : void {
    msgField.innerHTML = msg;
    msgField.classList.contains("kpro_web__display-none") && msg != "" ? msgField.classList.remove("kpro_web__display-none") : msgField.classList.add("kpro_web__display-none");
  }

  export function addSelectOption(selectField: HTMLSelectElement, options: string[]) : void {
    for(let i = 0; i < options.sort().length; i++) {
      let option = new Option(options[i],options[i]);
      selectField.add(option, undefined);
    }
  }
}