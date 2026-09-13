// Raster exports from the actual SVG assets. npm dependency: sharp 0.34+.
const fs = require('fs');
const path = require('path');
const sharp = require(process.env.BRIOSA_SHARP_MODULE || 'sharp');
const root = path.resolve(__dirname,'..');

async function main(){
  const manifest = JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
  for(const item of manifest.assets){
    if(item.kind==='master'||item.kind==='icon')continue;
    const dst = path.join(root,'png',item.file.replace(/\.svg$/,'.png'));
    fs.mkdirSync(path.dirname(dst),{recursive:true});
    const width=item.kind==='symbol'?1024:item.kind==='suite'?1200:1600;
    await sharp(path.join(root,item.file),{density:192}).resize({width}).png().toFile(dst);
  }
  for(const size of [16,24,32,48,64,128,256,512,1024]){
    const input=size<=32?'favicon.svg':'app-icon.svg';
    await sharp(path.join(root,'icons',input),{density:192}).resize(size,size).png().toFile(path.join(root,'icons',`briosa-icon-${size}.png`));
  }
  for(const [name,size] of [['apple-touch-icon',180],['android-chrome-192x192',192],['android-chrome-512x512',512]]){
    await sharp(path.join(root,'icons/app-icon-maskable.svg'),{density:192}).resize(size,size).png().toFile(path.join(root,'icons',name+'.png'));
  }
  await sharp(path.join(root,'preview.svg'),{density:96}).png().toFile(path.join(root,'preview.png'));
  await sharp(path.join(root,'qa/wordmark-trace.svg'),{density:72}).png().toFile(path.join(root,'qa/wordmark-trace.png'));
  // Compact proof sheet shows actual small-size pixels alongside the four themes.
  const panels=[];
  for(const [i,theme] of ['color','inverse','black','white'].entries()){
    const tile=await sharp({create:{width:760,height:300,channels:4,background:(theme==='inverse'||theme==='white')?'#003875':'#FFFFFF'}})
      .composite([{input:await sharp(path.join(root,`logos/briosa-horizontal-${theme}.svg`)).resize({width:700}).png().toBuffer(),left:30,top:50}]).png().toBuffer();
    panels.push({input:tile,left:(i%2)*760,top:Math.floor(i/2)*300});
  }
  let px=64;
  for(const size of [16,24,32,48,64,128]){
    panels.push({input:fs.readFileSync(path.join(root,`icons/briosa-icon-${size}.png`)),left:px,top:658});px+=size+65;
  }
  await sharp({create:{width:1520,height:844,channels:4,background:'#F2F2F2'}}).composite(panels).png().toFile(path.join(root,'qa/variant-and-size-proof.png'));
  console.log('Rendered PNG logo exports, platform icons, preview and QA sheets.');
}
main().catch(error=>{console.error(error);process.exit(1);});
