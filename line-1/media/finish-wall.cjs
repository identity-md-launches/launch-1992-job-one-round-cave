// Local image assembly only. No network, environment access, or task execution.
// Inputs must be the preceding wall and the image tool's additive edit, respectively.
const fs = require('node:fs');
const zlib = require('node:zlib');
const crypto = require('node:crypto');
const path = require('node:path');
const jpeg = require('./jpeg-encoder.cjs');
const signature = Buffer.from('89504e470d0a1a0a', 'hex');
const hash = b => crypto.createHash('sha256').update(b).digest('hex');

function local(file) {
  const full = path.resolve(file);
  const relative = path.relative(process.cwd(), full);
  if (relative.startsWith('..') || path.isAbsolute(relative)) throw Error('workspace paths only');
  return full;
}
function crc32(bytes) {
  let c = 0xffffffff;
  for (const byte of bytes) {
    c ^= byte;
    for (let i = 0; i < 8; i++) c = (c >>> 1) ^ (c & 1 ? 0xedb88320 : 0);
  }
  return (c ^ 0xffffffff) >>> 0;
}
function decode(bytes) {
  if (!bytes.subarray(0, 8).equals(signature)) throw Error('PNG required');
  let width, height, channels, parts = [];
  for (let offset = 8; offset < bytes.length;) {
    const size = bytes.readUInt32BE(offset);
    const type = bytes.toString('ascii', offset + 4, offset + 8);
    const data = bytes.subarray(offset + 8, offset + 8 + size);
    if (crc32(bytes.subarray(offset + 4, offset + 8 + size)) !== bytes.readUInt32BE(offset + 8 + size)) throw Error('bad CRC');
    if (type === 'IHDR') {
      width = data.readUInt32BE(0); height = data.readUInt32BE(4);
      if (width !== 1254 || height !== 1254 || data[8] !== 8 || ![2, 6].includes(data[9]) || data[12] !== 0) throw Error('1254px RGB/RGBA noninterlaced input required');
      channels = data[9] === 2 ? 3 : 4;
    }
    if (type === 'IDAT') parts.push(data);
    offset += size + 12;
    if (type === 'IEND') break;
  }
  const stride = width * channels;
  const raw = zlib.inflateSync(Buffer.concat(parts), {maxOutputLength: (stride + 1) * height});
  if (raw.length !== (stride + 1) * height) throw Error('bad raster length');
  const decoded = Buffer.alloc(stride * height);
  for (let y = 0; y < height; y++) {
    const filter = raw[y * (stride + 1)];
    if (filter > 4) throw Error('bad PNG filter');
    for (let x = 0; x < stride; x++) {
      const i = y * stride + x;
      const a = x >= channels ? decoded[i - channels] : 0;
      const b = y ? decoded[i - stride] : 0;
      const c = y && x >= channels ? decoded[i - stride - channels] : 0;
      const p = a + b - c, pa = Math.abs(p-a), pb = Math.abs(p-b), pc = Math.abs(p-c);
      const predictor = [0, a, b, Math.floor((a+b)/2), pa <= pb && pa <= pc ? a : pb <= pc ? b : c][filter];
      decoded[i] = (raw[y * (stride + 1) + x + 1] + predictor) & 255;
    }
  }
  const pixels = Buffer.alloc(width * height * 3);
  for (let i = 0; i < width * height; i++) {
    if (channels === 4 && decoded[i*channels+3] !== 255) throw Error('opaque input required');
    decoded.copy(pixels, i*3, i*channels, i*channels+3);
  }
  return {width, height, pixels};
}
function chunk(type, bytes) {
  const data = Buffer.concat([Buffer.from(type), bytes]);
  const result = Buffer.alloc(data.length + 8);
  result.writeUInt32BE(bytes.length, 0); data.copy(result, 4);
  result.writeUInt32BE(crc32(data), result.length - 4);
  return result;
}
function encode(image) {
  const header = Buffer.alloc(13);
  header.writeUInt32BE(image.width, 0); header.writeUInt32BE(image.height, 4);
  header[8] = 8; header[9] = 2;
  const stride = image.width * 3;
  const raw = Buffer.alloc((stride+1) * image.height);
  for (let y = 0; y < image.height; y++) {
    // Sub filtering keeps this rough, photographic source compact without loss.
    raw[y*(stride+1)] = 1;
    for (let x = 0; x < stride; x++) raw[y*(stride+1)+1+x] = (image.pixels[y*stride+x] - (x>=3 ? image.pixels[y*stride+x-3] : 0)) & 255;
  }
  return Buffer.concat([signature, chunk('IHDR', header), chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]);
}
function thumbnail(image) {
  const size = 512, data = Buffer.alloc(size * size * 4, 255);
  // Area-average each destination footprint, including fractional edge weights.
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
    const x0=x*image.width/size, x1=(x+1)*image.width/size;
    const y0=y*image.height/size, y1=(y+1)*image.height/size;
    const sums=[0,0,0]; let area=0;
    for(let sy=Math.floor(y0);sy<Math.ceil(y1);sy++) for(let sx=Math.floor(x0);sx<Math.ceil(x1);sx++) {
      const weight=(Math.min(x1,sx+1)-Math.max(x0,sx))*(Math.min(y1,sy+1)-Math.max(y0,sy));
      area+=weight;
      for(let c=0;c<3;c++) sums[c]+=image.pixels[(sy*image.width+sx)*3+c]*weight;
    }
    for(let c=0;c<3;c++) data[(y*size+x)*4+c]=Math.round(sums[c]/area);
  }
  return jpeg({width:size,height:size,data}, 82).data;
}
const clamp = value => Math.min(1, Math.max(0, value));
function mask(x, y) {
  // Only bare stone around the round-23 stepping stones and handprint. Isolated
  // disks deliberately exclude the old sun, dotted trail, snail and Pepe.
  const dots = [[848,851],[907,819],[966,780],[1009,748],
                [875,843],[891,833],[923,811],[941,799],[984,771]];
  let trail=0;
  for(const [cx,cy] of dots) trail=Math.max(trail,clamp((34-Math.hypot(x-cx,y-cy))/8));
  return trail;
}
function main() {
  const [oldPath, generatedPath, previewPath] = process.argv.slice(2);
  if(!oldPath || !generatedPath || !previewPath) throw Error('usage: node finish-wall.cjs PREVIOUS.png GENERATED.png PREVIEW.jpg');
  const oldBytes=fs.readFileSync(local(oldPath)), generated=decode(fs.readFileSync(local(generatedPath)));
  const original=decode(oldBytes), output={...original,pixels:Buffer.from(original.pixels)};
  let changed=0, protectedPixels=0;
  for(let y=0;y<original.height;y++) for(let x=0;x<original.width;x++) {
    const a=mask(x,y), offset=(y*original.width+x)*3;
    if(!a) protectedPixels++;
    for(let c=0;c<3;c++) output.pixels[offset+c]=Math.round(original.pixels[offset+c]*(1-a)+generated.pixels[offset+c]*a);
    if(!output.pixels.subarray(offset,offset+3).equals(original.pixels.subarray(offset,offset+3))) changed++;
  }
  const bytes=encode(output);
  if(!decode(bytes).pixels.equals(output.pixels)) throw Error('PNG round-trip failed');
  const preview=thumbnail(output);
  if(preview.length>100000) throw Error('preview exceeds 100 KB');
  fs.writeFileSync(local(generatedPath),bytes);
  fs.writeFileSync(local(oldPath),bytes);
  fs.writeFileSync(local(previewPath),preview);
  console.log(JSON.stringify({previous_sha256:hash(oldBytes),sha256:hash(bytes),width:original.width,height:original.height,
    changed_pixels:changed,protected_pixels:protectedPixels,total_pixels:original.width*original.height,
    png_bytes:bytes.length,jpeg_bytes:preview.length,jpeg_width:512,jpeg_height:512},null,2));
}
if(require.main===module) main();
module.exports={decode,encode,mask,thumbnail};
