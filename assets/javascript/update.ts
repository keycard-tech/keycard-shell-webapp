import KProJS from "kprojs";
import TransportWebHID from "kprojs-web-hid";
import Eth from "kprojs/lib/eth";
import Transport, { StatusCodes } from "kprojs/lib/transport";
import { TextStr } from "./text_str";
import { UIUtils } from "./ui_utils";
import { marked } from "marked";

const mediaPrefix = document.getElementById('db_updater__media-prefix') as HTMLInputElement;

const startUpdateScreen = document.getElementById("start-update-screen") as HTMLDivElement;
const connectDeviceScreen = document.getElementById("connect-device-screen") as HTMLDivElement;
const selectUpdateScreen = document.getElementById("select-update-screen") as HTMLDivElement;
const updateInProgressScreen = document.getElementById("update-in-progress-screen") as HTMLDivElement;
const updateSuccessScreen = document.getElementById("update-success-screen") as HTMLDivElement;
const updateFailedScreen = document.getElementById("update-failed-screen") as HTMLDivElement;

const startUpdateBtn =  document.getElementById("start-screen-btn") as HTMLButtonElement;
const transferDataBtn = document.getElementById("transfer-data-btn") as HTMLButtonElement;

const selectUpdatePrompt = document.getElementById("select-update-text") as HTMLSpanElement;
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

const updateSuccessMessage = document.getElementById("update-finished-success-message") as HTMLSpanElement;
const updateErrorMessage = document.getElementById("update-finished-err-message") as HTMLSpanElement;

const latestVersionColor = "#23ADA0";
const newestVersionColor = "##FF6400";
const fieldEnabled = "1";
const fieldDisabled = ".5";

const changelogContainer = document.getElementById("changelog") as HTMLSpanElement;

const updateProgressBar = document.getElementById("update-progress-bar") as HTMLProgressElement;

const mobileScreen = 600;

let isDBLatest : boolean;
let isFWLatest: boolean;

function preloadImage(imgUrl: string) : HTMLImageElement {
    let image = new Image();
    image.src = imgUrl;

    return image;
} 

function checkLatestVersion(deviceVersion: number, webVersion: number, updateStatus: HTMLSpanElement, checkField: HTMLInputElement, container: HTMLDivElement) : boolean {
    if(webVersion <= deviceVersion) {
        updateStatus.innerHTML = "Latest";
        updateStatus.style.color = latestVersionColor;
        checkField.disabled = true;
        container.style.opacity = ".5";
        return true;
    } else {
        updateStatus.innerHTML = "Newest version";
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

async function handleShellUpdate() : Promise<void> {
    let transport: Transport;
    let appEth: Eth;

    const fwContext = await fetch("../firmware/context").then((r) => r.json());
    const dbContext = await fetch("../context").then((r: any) => r.json());

    const dbData = await fetch(mediaPrefix.value + dbContext["db_path"]).then((r) => r.arrayBuffer());
    const fwData = await fetch(mediaPrefix.value + fwContext["fw_path"]).then((r) => r.arrayBuffer());
    const changelog = await fetch(mediaPrefix.value + fwContext["changelog_path"]).then((r) => r.text());

    changelogContainer.innerHTML = await marked.parse(changelog);

    fwUpdateCheckboxLabel.innerHTML = `${fwContext["version"]}`;
    dbUpdateCheckboxLabel.innerHTML = `${dbContext["version"]}`;

    const cableImage = preloadImage("../static/keycard_shell/img/cable.svg");
    const cablePluggingImage = preloadImage("../static/keycard_shell/img/cable_plugging.svg");
    const cablePluggedImage = preloadImage("../static/keycard_shell/img/cable_plugged.svg");

    transferDataBtn.disabled = !(dbUpdateCheckbox.checked || fwUpdateCheckbox.checked);

    window.onresize = () => handleMobileUI();
    handleMobileUI();

    startUpdateBtn.addEventListener("click", async (e) => {
        if(!appEth) {
            showNextScreen(startUpdateScreen, connectDeviceScreen);

            try {
                transport = await TransportWebHID.create();
                appEth = new KProJS.Eth(transport);

                let { erc20Version, fwVersion } = await appEth.getAppConfiguration();

                isDBLatest = checkLatestVersion(erc20Version, parseInt(dbContext["version"]), dbUpdateStatus, dbUpdateCheckbox, dbUpdateCheckboxContainer);
                isFWLatest = checkLatestVersion(parseInt(fwVersion.replaceAll(".", "")), parseInt(fwContext["version"].replaceAll(".", "")), fwUpdateStatus, fwUpdateCheckbox, fwUpdateCheckboxContainer);
            
                transport.on("disconnect", async () => {
                    const activeStep = document.getElementsByClassName(activeScreenClass)[0] as HTMLDivElement;
            
                    await transport.close();
                    transport = null;
                    appEth = null;
                            
                    updateErrorMessage.innerHTML = "Error connecting to device";
                    showNextScreen(activeStep, updateFailedScreen);
                });
                
                showNextScreen(connectDeviceScreen, selectUpdateScreen);
                pageTopContainer.classList.remove("keycard_shell__hide");
                pagePrompt.innerHTML = TextStr.shellConnectedPrompt;
            } catch(err) {
               console.log("here"); 
            }
        } else {
            pageTopContainer.classList.remove("keycard_shell__hide");
            pagePrompt.innerHTML = TextStr.shellConnectedPrompt; 
            showNextScreen(connectDeviceScreen, selectUpdateScreen); 
        }

        transferDataBtn.disabled = isDBLatest && isFWLatest;

        e.preventDefault();
    });

    dbUpdateCheckbox.addEventListener("change", () => {
        transferDataBtn.disabled = !(dbUpdateCheckbox.checked || fwUpdateCheckbox.checked );
        dbUpdateCheckboxContainer.style.opacity = dbUpdateCheckbox.checked ? fieldEnabled : fieldDisabled;
    });

    fwUpdateCheckbox.addEventListener("change", () => {
        transferDataBtn.disabled = !(dbUpdateCheckbox.checked || fwUpdateCheckbox.checked);
        fwUpdateCheckboxContainer.style.opacity = dbUpdateCheckbox.checked ? fieldEnabled : fieldDisabled;
    });

    transferDataBtn.addEventListener("click", async() => {
        showNextScreen(selectUpdateScreen, updateInProgressScreen);

        try {
            if(fwUpdateCheckbox.checked && !isFWLatest) {
                updateProgressBar.max = fwData.byteLength;
                progressPrompt.innerHTML = TextStr.progressFWPrompt + fwContext["version"];
                UIUtils.handleUpdateLoadProgress(transport, updateProgressBar, progressPercent);
                await appEth.loadFirmware(fwData);
                updateProgressBar.value = 0;
            }

            if(dbUpdateCheckbox.checked && !isDBLatest) {
                updateProgressBar.max = dbData.byteLength;
                progressPrompt.innerHTML = TextStr.progressDBPrompt + dbContext["version"];
                UIUtils.handleUpdateLoadProgress(transport, updateProgressBar, progressPercent);
                await appEth.loadERC20DB(dbData);
                updateProgressBar.value = 0;
            }

            showNextScreen(updateInProgressScreen, updateSuccessScreen);
            pagePrompt.innerHTML = TextStr.shellDisconnectPrompt;
        } catch(err) {
            pagePrompt.innerHTML = "";
            const activeStep = document.getElementsByClassName(activeScreenClass)[0] as HTMLDivElement;
            if (err instanceof KProJS.KProError.TransportOpenUserCancelled) {
                updateErrorMessage.innerHTML = "Error connecting to device";
                showNextScreen(activeStep, updateFailedScreen);
            } else {
                updateErrorMessage.innerHTML = (err.statusCode == StatusCodes.SECURITY_STATUS_NOT_SATISFIED) ? "Database update canceled by user" :  "Database transfer failed";
                showNextScreen(activeStep, updateFailedScreen);
            }
            await transport.close();
        }

        await transport.close();



    });

}

handleShellUpdate();