import * as esbuild from 'esbuild';
import { lessLoader } from 'esbuild-plugin-less';
import fs from 'node:fs';
import path from 'node:path';

let entryPoints = [
    { out: 'articleDetails', in: 'assets/article/details/index.js' },
    { out: 'articleArchive', in: 'assets/article/archive/index.js' },
    { out: 'careeropportunity', in: 'assets/careeropportunity/index.jsx' },
    { out: 'core', in: 'assets/core/index.js' },
    { out: 'contact', in: 'assets/contact/index.js' },
    { out: 'dashboard', in: 'assets/dashboard/core/index.js' },
    { out: 'dashboardApproval', in: 'assets/dashboard/approval/index.js' },
    { out: 'dashboardArticle', in: 'assets/dashboard/article/index.js' },
    { out: 'dashboardCareeropportunity', in: 'assets/dashboard/careeropportunity/index.js' },
    { out: 'dashboardChunks', in: 'assets/dashboard/chunks/index.js' },
    { out: 'dashboardEvents', in: 'assets/dashboard/events/index.js' },
    { out: 'dashboardGallery', in: 'assets/dashboard/gallery/index.js' },
    { out: 'dashboardGroups', in: 'assets/dashboard/groups/index.js' },
    { out: 'dashboardHobbies', in: 'assets/dashboard/hobbies/index.jsx' },
    { out: 'dashboardPosters', in: 'assets/dashboard/posters/index.js' },
    { out: 'dashboardWebshop', in: 'assets/dashboard/webshop/index.js' },
    { out: 'eventsArchive', in: 'assets/events/archive/index.js' },
    { out: 'eventsDetails', in: 'assets/events/details/index.js' },
    { out: 'eventsMail', in: 'assets/events/mail/index.js' },
    { out: 'feedback', in: 'assets/feedback/index.js' },
    { out: 'frontpage', in: 'assets/frontpage/index.jsx' },
    { out: 'hobbygroups', in: 'assets/hobbygroups/index.js' },
    { out: 'mailinglists', in: 'assets/mailinglists/index.js' },
    { out: 'profiles', in: 'assets/profiles/index.js' },
    { out: 'webshop', in: 'assets/webshop/index.js' },
    { out: 'wiki', in: 'assets/wiki/index.js' },
];

const outdir = "bundles/esbuild/";

let result = await esbuild.build({
    entryPoints: entryPoints,
    format: 'esm',
    bundle: true,
    outdir: outdir,
    outbase: "assets",
    entryNames: "[dir]/[name]-[hash]",
    assetNames: "[hash]",
    nodePaths: ["assets"],
    loader: {
        '.ttf': 'dataurl',
        '.eot': 'dataurl',
        '.woff': 'dataurl',
        '.woff2': 'dataurl',
        '.gif': 'dataurl',
        '.svg': 'dataurl',
    },
    plugins: [lessLoader()],
    platform: "browser",
    // we could use https://github.com/marcofugaro/browserslist-to-esbuild
    target: ['chrome109', 'firefox109', 'safari16', 'edge109'],
    splitting: true,
    minify: process.env.NODE_ENV === "production" || false,
    sourcemap: process.env.NODE_ENV === "production" || false,
    metafile: true
});

// We are very sneaky here, we used to use webpack, with https://github.com/django-webpack/webpack-bundle-tracker
// which produces a file similar to esbuild's `metafile`
/*
The end result should look like:
{
  "status": "done",
  "assets": {
    "060b2710bdbbe3dfe48b58d59bd5f1fb.svg": {
      "name": "060b2710bdbbe3dfe48b58d59bd5f1fb.svg",
      "path": "ABSOLUTE/onlineweb4/bundles/webpack/060b2710bdbbe3dfe48b58d59bd5f1fb.svg"
    },
    "careeropportunity-6aecb6e831ca4099e031.css": {
      "name": "careeropportunity-6aecb6e831ca4099e031.css",
      "path": "ABSOLUTE/onlineweb4/bundles/webpack/careeropportunity-6aecb6e831ca4099e031.css"
    },
    "careeropportunity-6aecb6e831ca4099e031.css.map": {
      "name": "careeropportunity-6aecb6e831ca4099e031.css.map",
      "path": "ABSOLUTE/onlineweb4/bundles/webpack/careeropportunity-6aecb6e831ca4099e031.css.map"
    },
    "careeropportunity-6aecb6e831ca4099e031.js": {
      "name": "careeropportunity-6aecb6e831ca4099e031.js",
      "path": "ABSOLUTE/onlineweb4/bundles/webpack/careeropportunity-6aecb6e831ca4099e031.js"
    },
    "careeropportunity-6aecb6e831ca4099e031.js.map": {
      "name": "careeropportunity-6aecb6e831ca4099e031.js.map",
      "path": "ABSOLUTE/onlineweb4/bundles/webpack/careeropportunity-6aecb6e831ca4099e031.js.map"
    },
  },
  "chunks": {
    "careeropportunity": [
      "careeropportunity-6aecb6e831ca4099e031.css",
      "careeropportunity-6aecb6e831ca4099e031.js",
      "careeropportunity-6aecb6e831ca4099e031.css.map",
      "careeropportunity-6aecb6e831ca4099e031.js.map"
    ],
  }
}

esbuild's metafile is defined here: https://esbuild.github.io/api/#metafile
we generate and write it automatically
and has this schema: 
interface Metafile {
  inputs: {
    [path: string]: {
      bytes: number
      imports: {
        path: string
        kind: string
        external?: boolean
        original?: string
      }[]
      format?: string
    }
  }
  outputs: {
    [path: string]: {
      bytes: number
      inputs: {
        [path: string]: {
          bytesInOutput: number
        }
      }
      imports: {
        path: string
        kind: string
        external?: boolean
      }[]
      exports: string[]
      entryPoint?: string
      cssBundle?: string
    }
  }
}
*/

let fake_webpack_stats_file = {
    status: "done",
    assets: {},
    chunks: {}
};

for (const [filepath, output] of Object.entries(result.metafile.outputs)) {
    let relative_filename = filepath.slice(outdir.length);
    let absPath = path.resolve(`./${filepath}`);
    fake_webpack_stats_file.assets[relative_filename] = {
        name: relative_filename,
        path: absPath,
    };

    // could use binary search, only one of the entrypoints is ever relevant
    for (const { out: chunk, in: entryPoint } of entryPoints) {
        let chunk_content = [];
        if (output.entryPoint && output.entryPoint === entryPoint) {
            chunk_content.push(relative_filename);
            let map = `${relative_filename}.map`;
            if (result.metafile.outputs[map]) {
                chunk_content.push(map);
            }
            if (output.cssBundle) {
                let relative_css_filename = output.cssBundle.slice(outdir.length)
                chunk_content.push(relative_css_filename);
                let map = `${relative_css_filename}.map`;
                if (result.metafile.outputs[map]) {
                    chunk_content.push(map);
                }
            }
        }
        if (!Array.isArray(fake_webpack_stats_file.chunks[chunk])) {
            fake_webpack_stats_file.chunks[chunk] = [];
        }
        for (const c of chunk_content) {
            fake_webpack_stats_file.chunks[chunk].push(c);
        }
    }

}

fs.writeFileSync('meta.json', JSON.stringify(result.metafile));
fs.writeFileSync('webpack-stats.json', JSON.stringify(fake_webpack_stats_file));
