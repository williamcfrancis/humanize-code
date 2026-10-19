import type { Serializer } from './types';

// ==========================================
// Serializer Registry
// ==========================================

/** Internal map that stores all of the registered serializers */
const registeredSerializersMap: Map<string, Serializer> = new Map<string, Serializer>();

/**
 * Registers a serializer under the given format name.
 * @param formatName - The name of the export format.
 * @param serializerFunction - The serializer function to register.
 */
export function registerSerializer(formatName: string, serializerFunction: Serializer): void {
  registeredSerializersMap.set(formatName, serializerFunction);
}

/**
 * Retrieves the serializer registered for the given format name.
 * @param formatName - The name of the export format.
 * @returns The serializer function, or undefined if none is registered.
 */
export function getSerializer(formatName: string): Serializer | undefined {
  return registeredSerializersMap.get(formatName);
}
