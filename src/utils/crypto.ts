// Cryptographic utilities for IDs and password handling

const PBKDF2_ITERATIONS = 120_000;
const PBKDF2_HASH = 'SHA-256';

function toHex(buffer: ArrayBuffer): string {
  return Array.from(new Uint8Array(buffer))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

export async function sha256(message: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(message);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  return toHex(hashBuffer);
}

export function generateSalt(length = 16): string {
  const bytes = new Uint8Array(length);
  crypto.getRandomValues(bytes);
  return toHex(bytes.buffer);
}

export async function hashPassword(password: string, salt: string): Promise<string> {
  const encoder = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    encoder.encode(password),
    { name: 'PBKDF2' },
    false,
    ['deriveBits']
  );

  const derivedBits = await crypto.subtle.deriveBits(
    {
      name: 'PBKDF2',
      salt: encoder.encode(salt),
      iterations: PBKDF2_ITERATIONS,
      hash: PBKDF2_HASH,
    },
    keyMaterial,
    256
  );

  return toHex(derivedBits);
}

export async function verifyPasswordHash(password: string, salt: string, expectedHash: string): Promise<boolean> {
  const computed = await hashPassword(password, salt);
  return computed === expectedHash;
}

export function validatePasswordStrength(password: string): string | null {
  if (password.length < 10) return 'Пароль должен быть не менее 10 символов';
  if (!/[A-Z]/.test(password)) return 'Добавьте хотя бы одну заглавную букву';
  if (!/[a-z]/.test(password)) return 'Добавьте хотя бы одну строчную букву';
  if (!/[0-9]/.test(password)) return 'Добавьте хотя бы одну цифру';
  if (!/[^A-Za-z0-9]/.test(password)) return 'Добавьте хотя бы один спецсимвол';
  return null;
}

export function generateId(): string {
  return crypto.randomUUID();
}
