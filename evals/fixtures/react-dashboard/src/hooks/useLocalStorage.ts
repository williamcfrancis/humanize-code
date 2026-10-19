import { useState } from 'react';

/**
 * Custom hook for persisting state in localStorage.
 * @param key - The localStorage key to use.
 * @param initialValue - The initial value to use if nothing is stored.
 * @returns A tuple containing the stored value and a setter function.
 */
export function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T) => void] {
  // Initialize the state with the value from localStorage, if available
  const [storedValue, setStoredValue] = useState<T>(() => {
    // Check if we are running in a browser environment
    if (typeof window === 'undefined') {
      return initialValue;
    }

    // Read the raw value from localStorage
    const rawValue = window.localStorage.getItem(key);

    try {
      // Parse the stored JSON value
      return rawValue !== null ? (JSON.parse(rawValue) as T) : initialValue;
    } catch (error) {
      // Handle JSON parsing errors gracefully
      console.error(`⚠️ Failed to parse localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  /**
   * Updates the stored value in both state and localStorage.
   * @param newValue - The new value to store.
   */
  const updateStoredValue = (newValue: T): void => {
    setStoredValue(newValue);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(key, JSON.stringify(newValue));
    }
  };

  // Return the stored value and the update function
  return [storedValue, updateStoredValue];
}
