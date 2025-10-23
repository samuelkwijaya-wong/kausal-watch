(function () {
  const ACTIONS_STATUS_CLASS = 'actions-status';
  const WAGTAIL_IS_LOADING_ATTRIBUTE = 'data-w-progress-loading-value';
  const WAGTAIL_LOADING_TEXT_ATTRIBUTE = 'data-w-progress-active-value';

  function waitForElements(selector) {
    return new Promise((resolve) => {
      if (document.querySelector(selector)) {
        return resolve(document.querySelectorAll(selector));
      }

      const observer = new MutationObserver((mutations) => {
        if (document.querySelector(selector)) {
          observer.disconnect();
          resolve(document.querySelectorAll(selector));
        }
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true,
      });
    });
  }

  async function fixDraftailDescribedByElements() {
    const elList = await waitForElements('.public-DraftEditor-content');
    elList.forEach((el) => {
      const hiddenInput = el.closest('.w-field__input')?.querySelector('input');
      if (hiddenInput == null) {
        return;
      }
      el.setAttribute(
        'aria-describedby',
        hiddenInput.getAttribute('aria-describedby'),
      );
    });
  }

  function addAttributesToNotificationMessages() {
    /*
    Fixes problem with screen reader not being able to detect Wagtail
    status messages.
     */
    const messageContainers = document.querySelectorAll('.messages');
    messageContainers.forEach(function (container) {
      container.setAttribute('role', 'alert');
      container.setAttribute('aria-live', 'assertive');
      container.setAttribute('aria-atomic', 'true');
      if (container.innerText) {
        container.setAttribute('aria-label', container.innerText);
      }
    });
  }

  function addAttributesToPublishActions() {
    const actionsBar = document.querySelector('.actions');

    if (actionsBar == null) {
      return;
    }

    const actionsStatus = document.createElement('div');

    actionsStatus.classList.add(ACTIONS_STATUS_CLASS, 'screen-reader-only');
    actionsStatus.setAttribute('aria-live', 'assertive');
    actionsStatus.setAttribute('role', 'status');
    actionsStatus.setAttribute('aria-atomic', 'true');
    actionsStatus.innerText = '';

    actionsBar.appendChild(actionsStatus);
  }

  function setupAriaBusyForProgressButtons() {
    setTimeout(() => {
      const status = document.querySelector(`.${ACTIONS_STATUS_CLASS}`);
      status.textContent = 'Saving...';
      console.log('Testing Saving alert after 5 seconds');

      setTimeout(() => {
        status.textContent = '';
      }, 1000);
    }, 5000);

    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (
          mutation.type === 'attributes' &&
          mutation.attributeName === WAGTAIL_IS_LOADING_ATTRIBUTE
        ) {
          const status = document.querySelector(`.${ACTIONS_STATUS_CLASS}`);
          const button = mutation.target;

          const isLoading =
            button.getAttribute(WAGTAIL_IS_LOADING_ATTRIBUTE) === 'true';

          if (isLoading) {
            const label = button.getAttribute(WAGTAIL_LOADING_TEXT_ATTRIBUTE);

            setTimeout(() => {
              status.textContent = label || '';
              status.setAttribute('aria-label', label || '');
            }, 100);
          }
        }
      });
    });

    // Observe all buttons with w-progress controller, for example the save and publish buttons
    const progressButtons = document.querySelectorAll(
      "[data-controller*='w-progress']",
    );

    progressButtons.forEach((button) => {
      observer.observe(button, {
        attributes: true,
        attributeFilter: [WAGTAIL_IS_LOADING_ATTRIBUTE],
      });
    });
  }

  function addActivePlanAccessibilityFlagToBodyClass(accessibilityLevel) {
    /*
    Some CSS styles must only be used when the plan explicitly requires them.
    Inject the accessibility class of the plan if it's not the default.
     */
    if (accessibilityLevel === 'default') {
      return;
    }
    const rootElement = document.body;
    rootElement.className = `${rootElement.className} watch-active-accessibility-level-${accessibilityLevel}`;
  }

  function injectAccessibilityFixes(accessibilityLevel) {
    addActivePlanAccessibilityFlagToBodyClass(accessibilityLevel);
    addAttributesToNotificationMessages();
    fixDraftailDescribedByElements();
    addAttributesToPublishActions();
    setupAriaBusyForProgressButtons();
  }

  const accessibilityScript = document.currentScript;
  const accessibilityLevel =
    accessibilityScript.dataset.activePlanAccessibilityLevel;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', (e) =>
      injectAccessibilityFixes(accessibilityLevel),
    );
    return;
  }
  injectAccessibilityFixes(activePlan);
})();
