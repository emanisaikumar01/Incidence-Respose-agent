document.addEventListener("DOMContentLoaded", () => {

    document.body.addEventListener(
        "htmx:beforeRequest",
        (event) => {
            const button = event.target.querySelector(
                "button[type='submit']"
            );

            if (button) {
                button.disabled = true;
            }
        }
    );


    document.body.addEventListener(
        "htmx:afterRequest",
        (event) => {
            const button = event.target.querySelector(
                "button[type='submit']"
            );

            if (button) {
                button.disabled = false;
            }
        }
    );


    document.body.addEventListener(
        "htmx:responseError",
        () => {

            const container =
                document.getElementById(
                    "toast-container"
                );

            if (!container) {
                return;
            }

            // Plain CSS (no Tailwind dependency).
            container.innerHTML = `
                <div style="
                    border: 1px solid rgba(239, 68, 68, 0.35);
                    border-radius: 0.9rem;
                    background: #0f172a;
                    color: #fca5a5;
                    padding: 0.75rem 1rem;
                    font-size: 0.875rem;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
                ">
                    Request failed. Please try again.
                </div>
            `;

            setTimeout(() => {
                container.innerHTML = "";
            }, 4000);
        }
    );

});