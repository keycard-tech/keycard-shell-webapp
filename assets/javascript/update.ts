import ShellJS from "shelljs";
import TransportWebHID from "shelljs-web-hid";
import Transport, { StatusCodes } from "shelljs/lib/transport";
import { TextStr } from "./text_str";
import { UIUtils } from "./ui_utils";
import Commands from "shelljs/lib/commands";

const mediaPrefix = document.getElementById('db_updater__media-prefix') as HTMLInputElement;

const startUpdateScreen = document.getElementById("start-update-screen") as HTMLDivElement;
const connectDeviceScreen = document.getElementById("connect-device-screen") as HTMLDivElement;
const selectUpdateScreen = document.getElementById("select-update-screen") as HTMLDivElement;
const updateInProgressScreen = document.getElementById("update-in-progress-screen") as HTMLDivElement;
const updateSuccessScreen = document.getElementById("update-success-screen") as HTMLDivElement;
const updateFailedScreen = document.getElementById("update-failed-screen") as HTMLDivElement;

const startUpdateBtn =  document.getElementById("start-screen-btn") as HTMLButtonElement;
const transferDataBtn = document.getElementById("transfer-data-btn") as HTMLButtonElement;

const progressPrompt = document.getElementById("update-progress-step-prompt") as HTMLSpanElement;
const progressPercent = document.getElementById("update-progress-percent") as HTMLSpanElement;

const hideScreenClass = "keycard_shell__display-none";
const activeScreenClass = "keycard_shell__active-step";

const fwUpdateCheckbox = document.getElementById("firmware-update") as HTMLInputElement;
const dbUpdateCheckbox = document.getElementById("db-update") as HTMLInputElement;

const fwUpdateCheckboxContainer = document.getElementById("firmware-update-container") as HTMLInputElement;
const dbUpdateCheckboxContainer = document.getElementById("db-update-container") as HTMLInputElement;

const fwUpdateCheckboxLabel = document.getElementById("firmware-update-label") as HTMLLabelElement;
const dbUpdateCheckboxLabel = document.getElementById("db-update-label") as HTMLLabelElement;

const fwUpdateStatus = document.getElementById("fw-update-status") as HTMLSpanElement;
const dbUpdateStatus = document.getElementById("db-update-status") as HTMLSpanElement;

const pagePrompt = document.getElementById("page-prompt") as HTMLSpanElement;
const pageTopContainer = document.getElementById("page-top-text") as HTMLDivElement;

const startScreenHeading = document.getElementById("start-screen-heading") as HTMLHeadElement;
const startScreenPrompt = document.getElementById("start-screen-prompt") as HTMLSpanElement;

const updateErrorMessage = document.getElementById("update-finished-err-message") as HTMLSpanElement;

const latestVersionColor = "#23ADA0";
const newestVersionColor = "##FF6400";
const fieldEnabled = "1";
const fieldDisabled = ".5";

const updateProgressBar = document.getElementById("update-progress-bar") as HTMLProgressElement;

const selectUpdateText = document.getElementById("select-update-text") as HTMLSpanElement;

const confirmUpdateInstructions = document.getElementById("finish-update-instructions") as HTMLDivElement;
const continueUpdateBtnContainer = document.getElementById("keycard_shell__update-next-btn-container") as HTMLDivElement;
const continueUpdateBtn = document.getElementById("update-next-btn") as HTMLButtonElement;
const paginator = document.getElementById("update-paginator") as HTMLSpanElement;

const mobileScreen = 959;

const bc = new BroadcastChannel('process_channel');

let isDBLatest : boolean;
let isFWLatest: boolean;

function checkLatestVersion(deviceVersion: number, webVersion: number, updateStatus: HTMLSpanElement, checkField: HTMLInputElement, container: HTMLDivElement) : boolean {
    if(webVersion <= deviceVersion) {
        updateStatus.innerHTML = TextStr.latest;
        updateStatus.style.color = latestVersionColor;
        checkField.disabled = true;
        container.style.opacity = ".5";
        return true;
    } else {
        updateStatus.innerHTML = TextStr.updateAvailable;
        updateStatus.style.color = newestVersionColor;
        return false;
    }
}

function showNextScreen(currentScreen: HTMLDivElement, nextScreen: HTMLDivElement) : void {
    currentScreen.classList.add(hideScreenClass);

    if(currentScreen.classList.contains(activeScreenClass)) {
        currentScreen.classList.remove(activeScreenClass);
    }
    
    nextScreen.classList.remove(hideScreenClass);
    nextScreen.classList.add(activeScreenClass);
}

function handleMobileUI() : void {
    if((window.innerWidth < mobileScreen)) {
        startScreenHeading.innerHTML = TextStr.startScreenHeadingMobile;
        startScreenPrompt.innerHTML = TextStr.startScreenPromptMobile;
    } else {
        startScreenHeading.innerHTML = TextStr.startScreenHeadingDesktop;
        startScreenPrompt.innerHTML = TextStr.startScreenPromptDesktop;
    }
}

function handleTransferStart(dataLength: number, promptText: string) : void {
    paginator.innerHTML = "1/2";
    updateProgressBar.classList.remove(hideScreenClass);
    progressPercent.classList.remove(hideScreenClass);
    updateProgressBar.max = dataLength;
    progressPrompt.innerHTML = promptText;
    continueUpdateBtnContainer.classList.contains(hideScreenClass) ? null : continueUpdateBtnContainer.classList.add(hideScreenClass);
}

function handleTransferCompleted (promptText: string) : void {
    paginator.innerHTML = "2/2";
    updateProgressBar.value = 0;
    progressPrompt.innerHTML = promptText;
    updateProgressBar.classList.add(hideScreenClass);
    progressPercent.classList.add(hideScreenClass);
    confirmUpdateInstructions.classList.remove(hideScreenClass);
}

function handleSuccessScreen() : void {
    bc.postMessage({state: 'success', process: 'update'});
    showNextScreen(updateInProgressScreen, updateSuccessScreen);
    pagePrompt.innerHTML = TextStr.shellDisconnectPrompt;
}

async function transferDatabase(transport: Transport, cmdSet: Commands, data: ArrayBuffer, startTransferPrompt: string, updateDBPrompt: string) : Promise<boolean> {
    handleTransferStart(data.byteLength, startTransferPrompt);

    if(transport) {
        UIUtils.handleUpdateLoadProgress(transport, updateProgressBar, progressPercent, () => handleTransferCompleted(updateDBPrompt));
        await cmdSet.loadDatabase(data);
    }

    return true;
}

async function transferFirmware(transport: Transport, cmdSet: Commands, data: ArrayBuffer, startTransferPrompt: string, updateFWPrompt: string) : Promise<void> {
    handleTransferStart(data.byteLength, startTransferPrompt);

    if(!transport && !cmdSet) {
        transport = await TransportWebHID.create();
        cmdSet = new Commands(transport);
    }

    UIUtils.handleUpdateLoadProgress(transport, updateProgressBar, progressPercent, () => handleTransferCompleted(updateFWPrompt));
    await cmdSet.loadFirmware(data); 

    handleSuccessScreen();
}

async function handleShellUpdate() : Promise<void> {
    let transport: Transport;
    let cmdSet: Commands;

    const fwContext = await fetch("../firmware/get-firmware").then((r) => r.json());
    const dbContext = await fetch("../get-db").then((r: any) => r.json());

    const dbData = await fetch(mediaPrefix.value + dbContext["db_path"]).then((r) => r.arrayBuffer());
    const fwData = await fetch(mediaPrefix.value + fwContext["fw_path"]).then((r) => r.arrayBuffer());

    fwUpdateCheckboxLabel.innerHTML = `${fwContext["version"]}`;
    dbUpdateCheckboxLabel.innerHTML = `${dbContext["version"]}`;

    transferDataBtn.disabled = !(dbUpdateCheckbox.checked || fwUpdateCheckbox.checked);

    handleMobileUI();

    window.addEventListener("resize", () => {
        handleMobileUI();
    });

    startUpdateBtn.addEventListener("click", async (e) => {
        if(!cmdSet) {
            showNextScreen(startUpdateScreen, connectDeviceScreen);

            try {
                transport = await TransportWebHID.create();
                cmdSet = new Commands(transport);

                let { dbVersion, fwVersion } = await cmdSet.getAppConfiguration();

                isDBLatest = checkLatestVersion(dbVersion, parseInt(dbContext["version"]), dbUpdateStatus, dbUpdateCheckbox, dbUpdateCheckboxContainer);
                isFWLatest = checkLatestVersion(UIUtils.parseFWVersion(fwVersion), UIUtils.parseFWVersion(fwContext["version"]), fwUpdateStatus, fwUpdateCheckbox, fwUpdateCheckboxContainer);
            
                transport.on("disconnect", async () => {
                    const activeStep = document.getElementsByClassName(activeScreenClass)[0] as HTMLDivElement;
            
                    await transport.close();
                    transport = null;
                    cmdSet = null;
                            
                    if(!activeStep.isEqualNode(updateSuccessScreen)) {
                        updateErrorMessage.innerHTML = "Error connecting to device";
                        showNextScreen(activeStep, updateFailedScreen);
                    }
                });
                
                showNextScreen(connectDeviceScreen, selectUpdateScreen);
                pageTopContainer.classList.remove("keycard_shell__hide");
                pagePrompt.innerHTML = TextStr.shellConnectedPrompt;


            } catch(err) {
               console.log("Connection error");
            }
        }

        selectUpdateText.innerHTML = (isDBLatest && isFWLatest) ? TextStr.noUpdateNeeded : TextStr.selectiveUpdate;
        transferDataBtn.style.display = (isDBLatest && isFWLatest) ? "none" : "inherit";
        e.preventDefault();
    });

    dbUpdateCheckbox.addEventListener("change", () => {
        let fwChecked = isFWLatest ? false : fwUpdateCheckbox.checked;
        transferDataBtn.disabled = !(dbUpdateCheckbox.checked || fwChecked);
        dbUpdateCheckboxContainer.style.opacity = dbUpdateCheckbox.checked ? fieldEnabled : fieldDisabled;
    });

    fwUpdateCheckbox.addEventListener("change", () => {
        let dbChecked = isDBLatest ? false : dbUpdateCheckbox.checked;
        transferDataBtn.disabled = !(fwUpdateCheckbox.checked || dbChecked);
        fwUpdateCheckboxContainer.style.opacity = fwUpdateCheckbox.checked ? fieldEnabled : fieldDisabled;
    });

    continueUpdateBtn.addEventListener("click", async (e) => {
        await transferFirmware(null, null, fwData, TextStr.progressFWPrompt + fwContext["version"], TextStr.fwTransferedText);
        e.preventDefault();
    });

    transferDataBtn.addEventListener("click", async() => {
        showNextScreen(selectUpdateScreen, updateInProgressScreen);

        try {
            if(dbUpdateCheckbox.checked && !isDBLatest) {
                let dbUpdateCompleted  = await transferDatabase(transport, cmdSet, dbData, TextStr.progressDBPrompt + dbContext["version"], TextStr.dbTransferedText);
                if(dbUpdateCompleted && (fwUpdateCheckbox.checked && !isFWLatest)) {
                    confirmUpdateInstructions.classList.add(hideScreenClass);
                    continueUpdateBtnContainer.classList.remove(hideScreenClass);
                } else {
                    handleSuccessScreen();
                }
            } else if(fwUpdateCheckbox.checked && !isFWLatest) {
                await transferFirmware(transport, cmdSet, fwData, TextStr.progressFWPrompt + fwContext["version"], TextStr.fwTransferedText);
            }
        } catch(err) {
            pagePrompt.innerHTML = "";
            const activeStep = document.getElementsByClassName(activeScreenClass)[0] as HTMLDivElement;
            if (err instanceof ShellJS.ShellError.TransportOpenUserCancelled) {
                updateErrorMessage.innerHTML = "Error connecting to device";
                showNextScreen(activeStep, updateFailedScreen);
            } else {
                updateErrorMessage.innerHTML = (err.statusCode == StatusCodes.SECURITY_STATUS_NOT_SATISFIED) ? TextStr.updateCanceled:  TextStr.updateFailed;
                showNextScreen(activeStep, updateFailedScreen);
            }
            await transport.close();
        }

        await transport.close();
    });

}

handleShellUpdate();