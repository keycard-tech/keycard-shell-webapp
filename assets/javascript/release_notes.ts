import { marked } from "marked";

const mediaPrefix = document.getElementById('db_updater__media-prefix') as HTMLInputElement;

const releaseNotesContainer = document.getElementById("release-notes-container") as HTMLDialogElement;
const fwContainerClass = "keycard_shell__fw-release-notes";
const fwContainerId = "fw-rn-";

const fwVersionContainerClass = "keycard_shell__fw-version-container";
const fwVersionId = "fw-version-container-";

const fwChangelogContainerClass = "keycard_shell__fw-changelog-container";
const fwChangelogId = "fw-changelog-container-";

async function renderReleaseNotesUI(fw: any, fwId: number, changelog: string) : Promise<void> {
    const fwVersionContent = `<h2 class="keycard_shell__fw-version-content" id="v${fw["version"]}">${fw["version"]}</h2>`;
    const fwCreationDate = new Date(changelog.substring(0, changelog.indexOf('\n')));

    const fwRNContainer = document.createElement("div");
    fwRNContainer.classList.add(fwContainerClass);
    fwRNContainer.id = fwContainerId + fwId.toString();

    const fwVersionContainer = document.createElement("div");
    fwVersionContainer.classList.add(fwVersionContainerClass);
    fwVersionContainer.id = fwVersionId + fw["version"] as string;
    fwVersionContainer.innerHTML = fwVersionContent;

    const fwVersionChangelog = document.createElement("div");
    fwVersionChangelog.classList.add(fwChangelogContainerClass);
    fwVersionChangelog.id = fwChangelogId + fw["version"] as string;

    if(fwCreationDate) {
        let formattedDate = fwCreationDate.getDate() + " " + fwCreationDate.toLocaleString('en-GB', { month: 'short' }) + ", " + fwCreationDate.getFullYear();
        changelog = changelog.substring(changelog.indexOf('\n'));
        fwVersionChangelog.innerHTML = `<span class="keycard_shell__fw-release-date">${formattedDate}</span>`
    }

    fwVersionChangelog.innerHTML = fwVersionChangelog.innerHTML + await marked(changelog);

    fwRNContainer.appendChild(fwVersionContainer);
    fwRNContainer.appendChild(fwVersionChangelog);
    releaseNotesContainer.appendChild(fwRNContainer);
}

async function handleReleaseNotes() : Promise<void> {
    const fwReleaseNotes = await fetch("../firmware/fws-context").then((r) => r.json());
    
    for (let i = 0; i < fwReleaseNotes.length; i++) {
        let changelogPath = fwReleaseNotes[i]["changelog"];
        const changelog = await fetch(mediaPrefix.value + changelogPath).then((r) => r.text());
        await renderReleaseNotesUI(fwReleaseNotes[i], i, changelog);
    }
}

handleReleaseNotes();