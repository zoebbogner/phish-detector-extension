// utils/cache.js
// Utility for bounded-size (LRU-ish) Map cache operations

/**
 * Inserts a key→value into a Map, enforcing a maximum size.
 * If the key already exists, it's moved to the most-recent position.
 * When capacity is exceeded, the oldest entry is evicted.
 *
 * @param {Map<any, any>} map - The Map to operate on.
 * @param {any} key - The key to insert or update.
 * @param {any} value - The value to associate with the key.
 * @param {number} maxSize - Maximum number of entries to keep in the map.
 */
export function putWithLimit(map, key, value, maxSize = 10) {
    // If key exists, remove it so insertion order resets
    if (map.has(key)) {
        map.delete(key);
    }

    // Insert as newest entry
    map.set(key, value);

    // Evict oldest entry if over capacity
    if (map.size > maxSize) {
        const oldestKey = map.keys().next().value;
        map.delete(oldestKey);
    }
}
