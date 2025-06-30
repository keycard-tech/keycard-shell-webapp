import {URDecoder, UREncoder} from '@ngraveio/bc-ur'

export namespace QRUtils {

  export function toBuffer(arrayBuffer: ArrayBuffer) : Buffer {
    const buffer = Buffer.alloc(arrayBuffer.byteLength);
    const view = new Uint8Array(arrayBuffer);

    for (let i = 0; i < buffer.length; ++i) {
      buffer[i] = view[i];
    }

    return buffer;
  }

  export function displayQRPart(part: any, qrCanv: any, size: number) : void {
    qrCanv.set({
      size: size,
      value: part
    });
  }

  export function generateQRPart(encoder: {enc: UREncoder}, qrCanv: any, timeout: boolean, size: number) : void {
    if(encoder.enc) {
      let part = encoder.enc.nextPart();
      qrCanv.padding = (encoder.enc.fragmentsLength == 1 && encoder.enc.messageLength >= 200) ? 42 : null;
      displayQRPart(part.toUpperCase(), qrCanv, size);
    }

    if(timeout) {
      setTimeout(() => {generateQRPart(encoder, qrCanv, true, size)}, 500);
    }
  }

  export function encodeChallenge(challenge: Uint8Array) : Buffer {
    return Buffer.from([0xa2, 0x01, 0x01, 0x06, 0x58, 0x20, ...challenge]);
  }

  export function decodeQR(decoder: URDecoder, qr: string) : Buffer {
    while (!decoder.isComplete()) {
      decoder.receivePart(qr);
    }

    if (decoder.isSuccess()) {
      const ur = decoder.resultUR();
      return ur.decodeCBOR();
    }
    else {
      const error = decoder.resultError()
      console.log('Error while decoding', error)
      return;
    }
  }
}