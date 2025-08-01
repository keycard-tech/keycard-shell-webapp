const mediaPrefix = document.getElementById('db_updater__media-prefix') as HTMLInputElement;

async function handleAirGappedUpdate() : Promise<void> {
    const fwContext = await fetch("../firmware/context").then((r) => r.json());
    const dbContext = await fetch("../context").then((r: any) => r.json());
}

handleAirGappedUpdate();