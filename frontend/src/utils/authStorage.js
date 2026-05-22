/**
 * Auth storage helpers — clears client-side cached auth state
 */

export function clearAllCookies() {
  if (typeof document === "undefined") return;
  const cookies = document.cookie.split(";");
  for (const cookie of cookies) {
    const eqPos = cookie.indexOf("=");
    const name = eqPos > -1 ? cookie.slice(0, eqPos) : cookie;
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
  }
}

export function clearAuthStorage() {
  try {
    localStorage.clear();
  } catch {
    // ignore storage access errors
  }

  try {
    sessionStorage.clear();
  } catch {
    // ignore storage access errors
  }

  clearAllCookies();
}
