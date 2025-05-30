// rollup.config.mjs
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';

export default {
    input: ['content.js', 'utils/content_features.js'],
    plugins: [
        resolve({ browser: true }),
        commonjs()
    ],
    output: {
        dir: 'dist/content',
        format: 'es',
        entryFileNames: '[name].bundle.js',
        chunkFileNames: '[name]-[hash].js',
        exports: 'auto'
    }
};