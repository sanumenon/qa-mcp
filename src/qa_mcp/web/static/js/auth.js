(() => {
    "use strict";

    const originalFetch = window.fetch.bind(window);
    const csrfToken = () => {
        const match = document.cookie.match(/(?:^|;\s*)qa_csrf=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : "";
    };

    const showAccessDenied = () => {
        let notice = document.getElementById("qa-access-denied");
        if (!notice) {
            notice = document.createElement("div");
            notice.id = "qa-access-denied";
            notice.className = "error";
            notice.setAttribute("role", "alert");
            notice.textContent = "You do not have access to this project or action.";
            (document.querySelector("main") || document.body).prepend(notice);
        }
    };

    window.fetch = async (input, init = {}) => {
        const requestMethod = init.method || (input instanceof Request ? input.method : "GET");
        const method = String(requestMethod).toUpperCase();
        const options = { credentials: "same-origin", ...init };
        if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
            const headers = new Headers(options.headers || (input instanceof Request ? input.headers : undefined));
            const csrf = csrfToken();
            if (csrf) headers.set("X-CSRF-Token", csrf);
            options.headers = headers;
        }
        const response = await originalFetch(input, options);
        if (response.status === 401 && !location.pathname.startsWith("/auth/")) {
            location.assign("/auth/login");
        }
        if (response.status === 403) showAccessDenied();
        return response;
    };

    document.addEventListener("DOMContentLoaded", async () => {
        const navigation = document.querySelector(".workflow-navigation");
        if (!navigation) return;
        const identity = document.createElement("span");
        identity.className = "auth-identity";
        identity.setAttribute("role", "status");
        identity.textContent = "Signed in";
        navigation.append(identity);
        try {
            const response = await originalFetch("/api/auth/me", { credentials: "same-origin" });
            if (response.status === 401) {
                identity.textContent = "Session expired";
                return;
            }
            if (!response.ok) throw new Error("identity unavailable");
            const actor = await response.json();
            identity.textContent = actor.email || "Local development user";
            const signOut = document.createElement("button");
            signOut.type = "button";
            signOut.className = "auth-sign-out";
            signOut.textContent = "Sign out";
            signOut.addEventListener("click", async () => {
                await window.fetch("/auth/logout", { method: "POST" });
                location.assign("/auth/login");
            });
            navigation.append(signOut);
        } catch (_error) {
            identity.textContent = "Identity status unavailable";
        }
    });
})();
