const translations = {
  en: {
    eyebrow: 'ML-powered estimation',
    title: 'Insurance Cost Predictor',
    subtitle: 'Fill in the form to estimate the insurance premium using a trained regression model.',
    ageLabel: 'Age',
    sexLabel: 'Sex',
    maleOption: 'Male',
    femaleOption: 'Female',
    bmiLabel: 'Body Mass Index (BMI)',
    childrenLabel: 'Children',
    smokerLabel: 'Smoker',
    yesOption: 'Yes',
    noOption: 'No',
    regionLabel: 'Region',
    southeastOption: 'Southeast',
    southwestOption: 'Southwest',
    northeastOption: 'Northeast',
    northwestOption: 'Northwest',
    submitButton: 'Predict',
    resultTitle: 'Estimated insurance cost',
    resultMessage: 'The estimate for this profile is:',
    loading: 'Calculating...',
    error: 'We could not generate a prediction. Please try again.',
    ageHelp: 'Example: 35 years',
    bmiHelp: 'Example: 24.5',
    childrenHelp: 'Example: 2',
    agePlaceholder: 'Example: 35 years',
    bmiPlaceholder: 'Example: 24.5',
    childrenPlaceholder: 'Example: 2',
    languageLabel: 'Language',
    footerText: 'Built by Michael Acosta',
    linkedinLabel: 'Visit LinkedIn profile',
    githubLabel: 'Visit GitHub profile',
  },
  es: {
    eyebrow: 'Estimación con Machine Learning',
    title: 'Predictor de costo de seguro',
    subtitle: 'Completa el formulario para estimar el costo del seguro con un modelo de regresión entrenado.',
    ageLabel: 'Edad',
    sexLabel: 'Sexo',
    maleOption: 'Hombre',
    femaleOption: 'Mujer',
    bmiLabel: 'Índice de Masa Corporal (IMC)',
    childrenLabel: 'Hijos',
    smokerLabel: 'Fumador',
    yesOption: 'Sí',
    noOption: 'No',
    regionLabel: 'Región',
    southeastOption: 'Sureste',
    southwestOption: 'Suroeste',
    northeastOption: 'Noreste',
    northwestOption: 'Noroeste',
    submitButton: 'Predecir',
    resultTitle: 'Costo estimado del seguro',
    resultMessage: 'La estimación para este perfil es:',
    loading: 'Calculando...',
    error: 'No pudimos generar una predicción. Inténtalo de nuevo.',
    ageHelp: 'Ejemplo: 35 años',
    bmiHelp: 'Ejemplo: 24.5',
    childrenHelp: 'Ejemplo: 2',
    agePlaceholder: 'Ejemplo: 35 años',
    bmiPlaceholder: 'Ejemplo: 24.5',
    childrenPlaceholder: 'Ejemplo: 2',
    languageLabel: 'Idioma',
    footerText: 'Creado por Michael Acosta',
    linkedinLabel: 'Visitar perfil de LinkedIn',
    githubLabel: 'Visitar perfil de GitHub',
  },
};

const ui = {
  form: document.getElementById('prediction-form'),
  resultCard: document.getElementById('result-card'),
  resultValue: document.getElementById('result-value'),
  resultMessage: document.getElementById('result-message'),
};

let currentLanguage = getInitialLanguage();

function getInitialLanguage() {
  const saved = window.localStorage.getItem('insurance-app-language');
  if (saved === 'es' || saved === 'en') {
    return saved;
  }

  const language = navigator.language || 'en';
  return language.toLowerCase().startsWith('es') ? 'es' : 'en';
}

function getLanguage() {
  return currentLanguage;
}

function setLanguage(lang) {
  currentLanguage = lang;
  window.localStorage.setItem('insurance-app-language', lang);
  applyTranslations();
}

function applyTranslations() {
  const lang = getLanguage();
  document.documentElement.lang = lang;
  document.title = lang === 'es' ? 'Predictor de costo de seguro' : 'Insurance Cost Predictor';

  document.querySelectorAll('[data-i18n]').forEach((element) => {
    const key = element.getAttribute('data-i18n');
    if (translations[lang][key]) {
      element.textContent = translations[lang][key];
    }
  });

  document.querySelectorAll('[data-i18n-placeholder]').forEach((element) => {
    const key = element.getAttribute('data-i18n-placeholder');
    if (translations[lang][key]) {
      element.setAttribute('placeholder', translations[lang][key]);
    }
  });

  document.querySelectorAll('[data-i18n-aria]').forEach((element) => {
    const key = element.getAttribute('data-i18n-aria');
    if (translations[lang][key]) {
      element.setAttribute('aria-label', translations[lang][key]);
    }
  });

  document.querySelectorAll('option[data-i18n]').forEach((option) => {
    const key = option.getAttribute('data-i18n');
    if (translations[lang][key]) {
      option.textContent = translations[lang][key];
    }
  });

  document.querySelectorAll('.lang-btn').forEach((button) => {
    const isActive = button.getAttribute('data-lang') === lang;
    button.classList.toggle('is-active', isActive);
    button.setAttribute('aria-pressed', isActive ? 'true' : 'false');
  });
}

function formatCurrency(value, lang) {
  return new Intl.NumberFormat(lang === 'es' ? 'es-ES' : 'en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value);
}

ui.form?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const lang = getLanguage();
  const formData = new FormData(ui.form);
  const payload = Object.fromEntries(formData.entries());

  ui.resultCard.hidden = false;
  ui.resultValue.textContent = translations[lang].loading;
  ui.resultMessage.textContent = '';

  try {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      throw new Error(data.error || translations[lang].error);
    }

    ui.resultValue.textContent = formatCurrency(data.prediction, lang);
    ui.resultMessage.textContent = `${translations[lang].resultMessage} ${formatCurrency(data.prediction, lang)}`;
  } catch (error) {
    ui.resultValue.textContent = translations[lang].error;
    ui.resultMessage.textContent = '';
  }
});

document.querySelectorAll('.lang-btn').forEach((button) => {
  button.addEventListener('click', () => {
    setLanguage(button.getAttribute('data-lang'));
  });
});

applyTranslations();
