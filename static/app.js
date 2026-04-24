const elements = {
  scrollProgress: document.querySelector("#scrollProgress"),
  brandName: document.querySelector("#brandName"),
  ownerNameHero: document.querySelector("#ownerNameHero"),
  heroCanvas: document.querySelector("#heroCanvas"),
  heroIntro: document.querySelector("#heroIntro"),
  heroTitle: document.querySelector("#heroTitle"),
  heroBlurb: document.querySelector("#heroBlurb"),
  ownerRole: document.querySelector("#ownerRole"),
  ownerLocation: document.querySelector("#ownerLocation"),
  availabilityLabel: document.querySelector("#availabilityLabel"),
  primaryCta: document.querySelector("#primaryCta"),
  secondaryCta: document.querySelector("#secondaryCta"),
  aboutTitle: document.querySelector("#aboutTitle"),
  aboutBody: document.querySelector("#aboutBody"),
  githubLink: document.querySelector("#githubLink"),
  linkedinLink: document.querySelector("#linkedinLink"),
  twitterLink: document.querySelector("#twitterLink"),
  resumeLink: document.querySelector("#resumeLink"),
  emailLink: document.querySelector("#emailLink"),
  phoneLink: document.querySelector("#phoneLink"),
  statGrid: document.querySelector("#statGrid"),
  projectGrid: document.querySelector("#projectGrid"),
  experienceList: document.querySelector("#experienceList"),
  skillsCloud: document.querySelector("#skillsCloud"),
  testimonialGrid: document.querySelector("#testimonialGrid"),
  dashboardMetrics: document.querySelector("#dashboardMetrics"),
  contactForm: document.querySelector("#contactForm"),
  contactName: document.querySelector("#contactName"),
  contactEmail: document.querySelector("#contactEmail"),
  contactCompany: document.querySelector("#contactCompany"),
  contactBudget: document.querySelector("#contactBudget"),
  contactMessage: document.querySelector("#contactMessage"),
  contactFeedback: document.querySelector("#contactFeedback"),
  adminToggleBtn: document.querySelector("#adminToggleBtn"),
  closeDrawerBtn: document.querySelector("#closeDrawerBtn"),
  drawerBackdrop: document.querySelector("#drawerBackdrop"),
  adminDrawer: document.querySelector("#adminDrawer"),
  authPanel: document.querySelector("#authPanel"),
  adminPanel: document.querySelector("#adminPanel"),
  authHeading: document.querySelector("#authHeading"),
  authForm: document.querySelector("#authForm"),
  authName: document.querySelector("#authName"),
  authEmail: document.querySelector("#authEmail"),
  authPassword: document.querySelector("#authPassword"),
  authSubmitBtn: document.querySelector("#authSubmitBtn"),
  authSwitchBtn: document.querySelector("#authSwitchBtn"),
  authFeedback: document.querySelector("#authFeedback"),
  adminGreeting: document.querySelector("#adminGreeting"),
  logoutBtn: document.querySelector("#logoutBtn"),
  saveAllBtn: document.querySelector("#saveAllBtn"),
  adminFeedback: document.querySelector("#adminFeedback"),
  siteSettingsForm: document.querySelector("#siteSettingsForm"),
  ownerNameInput: document.querySelector("#ownerNameInput"),
  ownerRoleInput: document.querySelector("#ownerRoleInput"),
  ownerLocationInput: document.querySelector("#ownerLocationInput"),
  heroIntroInput: document.querySelector("#heroIntroInput"),
  heroTitleInput: document.querySelector("#heroTitleInput"),
  heroBlurbInput: document.querySelector("#heroBlurbInput"),
  aboutTitleInput: document.querySelector("#aboutTitleInput"),
  aboutBodyInput: document.querySelector("#aboutBodyInput"),
  primaryCtaLabelInput: document.querySelector("#primaryCtaLabelInput"),
  primaryCtaUrlInput: document.querySelector("#primaryCtaUrlInput"),
  secondaryCtaLabelInput: document.querySelector("#secondaryCtaLabelInput"),
  secondaryCtaUrlInput: document.querySelector("#secondaryCtaUrlInput"),
  emailInput: document.querySelector("#emailInput"),
  phoneInput: document.querySelector("#phoneInput"),
  githubUrlInput: document.querySelector("#githubUrlInput"),
  linkedinUrlInput: document.querySelector("#linkedinUrlInput"),
  twitterUrlInput: document.querySelector("#twitterUrlInput"),
  resumeUrlInput: document.querySelector("#resumeUrlInput"),
  availabilityLabelInput: document.querySelector("#availabilityLabelInput"),
  yearsExperienceInput: document.querySelector("#yearsExperienceInput"),
  projectsCompletedInput: document.querySelector("#projectsCompletedInput"),
  happyClientsInput: document.querySelector("#happyClientsInput"),
  projectEditorList: document.querySelector("#projectEditorList"),
  experienceEditorList: document.querySelector("#experienceEditorList"),
  skillEditorList: document.querySelector("#skillEditorList"),
  testimonialEditorList: document.querySelector("#testimonialEditorList"),
  messageList: document.querySelector("#messageList"),
  addProjectBtn: document.querySelector("#addProjectBtn"),
  addExperienceBtn: document.querySelector("#addExperienceBtn"),
  addSkillBtn: document.querySelector("#addSkillBtn"),
  addTestimonialBtn: document.querySelector("#addTestimonialBtn"),
  scopeChips: document.querySelectorAll(".scope-chip"),
};

const templates = {
  projectCard: document.querySelector("#projectCardTemplate"),
  timelineItem: document.querySelector("#timelineItemTemplate"),
  skillChip: document.querySelector("#skillChipTemplate"),
  testimonial: document.querySelector("#testimonialTemplate"),
  dashboardMetric: document.querySelector("#dashboardMetricTemplate"),
};

const state = {
  csrfToken: "",
  authMode: "login",
  session: null,
  publicData: null,
  adminData: null,
};

function uid() {
  return self.crypto?.randomUUID?.() || `id-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

async function apiFetch(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(state.csrfToken ? { "X-CSRF-Token": state.csrfToken } : {}),
      ...(options.headers || {}),
    },
    ...options,
  });
  const data = await response.json();
  if (data?.csrfToken) {
    state.csrfToken = data.csrfToken;
  }
  if (!response.ok) {
    throw new Error(data?.error || "Request failed.");
  }
  return data;
}

async function bootstrap() {
  bindEvents();
  const [publicData, sessionData] = await Promise.all([apiFetch("/api/public-site"), apiFetch("/api/session")]);
  state.publicData = publicData;
  state.session = sessionData.user;
  state.adminData = sessionData.admin || null;
  renderPublic();
  renderAdminState();
  startHeroCanvas();
  updateScrollProgress();
}

function bindEvents() {
  window.addEventListener("scroll", updateScrollProgress, { passive: true });
  elements.adminToggleBtn.addEventListener("click", openDrawer);
  elements.closeDrawerBtn.addEventListener("click", closeDrawer);
  elements.drawerBackdrop.addEventListener("click", closeDrawer);
  elements.authForm.addEventListener("submit", handleAuthSubmit);
  elements.authSwitchBtn.addEventListener("click", toggleAuthMode);
  elements.logoutBtn.addEventListener("click", handleLogout);
  elements.contactForm.addEventListener("submit", handleContactSubmit);
  elements.saveAllBtn.addEventListener("click", saveAdminContent);
  elements.addProjectBtn.addEventListener("click", () => addEditorCard("project"));
  elements.addExperienceBtn.addEventListener("click", () => addEditorCard("experience"));
  elements.addSkillBtn.addEventListener("click", () => addEditorCard("skill"));
  elements.addTestimonialBtn.addEventListener("click", () => addEditorCard("testimonial"));
  elements.scopeChips.forEach((button) => button.addEventListener("click", () => applyScopePrompt(button)));
}

function updateScrollProgress() {
  const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
  const progress = maxScroll > 0 ? window.scrollY / maxScroll : 0;
  elements.scrollProgress.style.transform = `scaleX(${Math.min(1, Math.max(0, progress))})`;
}

function applyScopePrompt(button) {
  const prompt = button.dataset.scope || "";
  const current = elements.contactMessage.value.trim();
  elements.contactMessage.value = current ? `${current}\n\n${prompt}` : prompt;
  elements.contactMessage.focus();
  elements.scopeChips.forEach((chip) => chip.classList.toggle("is-active", chip === button));
}

function openDrawer() {
  elements.drawerBackdrop.classList.remove("hidden");
  elements.adminDrawer.classList.remove("hidden");
}

function closeDrawer() {
  elements.drawerBackdrop.classList.add("hidden");
  elements.adminDrawer.classList.add("hidden");
}

function toggleAuthMode() {
  state.authMode = state.authMode === "login" ? "register" : "login";
  elements.authHeading.textContent = state.authMode === "login" ? "Sign in" : "Create owner account";
  elements.authSubmitBtn.textContent = state.authMode === "login" ? "Sign in" : "Register";
  elements.authSwitchBtn.textContent =
    state.authMode === "login" ? "Need the first admin account? Register" : "Already have an account? Sign in";
  elements.authName.parentElement.classList.toggle("hidden", state.authMode === "login");
  elements.authFeedback.textContent = "";
}

function updateLink(element, value, fallbackText, prefix = "") {
  element.href = prefix ? `${prefix}${value}` : value || "#";
  element.textContent = fallbackText;
}

function renderPublic() {
  const data = state.publicData;
  if (!data) {
    return;
  }
  const site = data.site;
  elements.brandName.textContent = site.ownerName;
  elements.ownerNameHero.textContent = site.ownerName;
  elements.heroIntro.textContent = site.heroIntro;
  elements.heroTitle.textContent = site.heroTitle;
  elements.heroBlurb.textContent = site.heroBlurb;
  elements.ownerRole.textContent = site.ownerRole;
  elements.ownerLocation.textContent = site.ownerLocation;
  elements.availabilityLabel.textContent = site.availabilityLabel;
  elements.primaryCta.textContent = site.primaryCtaLabel;
  elements.primaryCta.href = site.primaryCtaUrl;
  elements.secondaryCta.textContent = site.secondaryCtaLabel;
  elements.secondaryCta.href = site.secondaryCtaUrl;
  elements.aboutTitle.textContent = site.aboutTitle;
  elements.aboutBody.textContent = site.aboutBody;
  updateLink(elements.githubLink, site.githubUrl, "GitHub");
  updateLink(elements.linkedinLink, site.linkedinUrl, "LinkedIn");
  updateLink(elements.twitterLink, site.twitterUrl, "X");
  updateLink(elements.resumeLink, site.resumeUrl, "Resume");
  updateLink(elements.emailLink, site.email, site.email, "mailto:");
  updateLink(elements.phoneLink, site.phone, site.phone, "tel:");

  renderStats(site);
  renderProjects(data.projects || []);
  renderExperience(data.experiences || []);
  renderSkills(data.skills || []);
  renderTestimonials(data.testimonials || []);
}

function startHeroCanvas() {
  const canvas = elements.heroCanvas;
  if (!canvas || canvas.dataset.running === "true") {
    return;
  }
  canvas.dataset.running = "true";
  const context = canvas.getContext("2d");
  const labels = ["CALL", "SLOAD", "AUTH", "PROOF", "EVM", "REVERT", "SIG", "TRACE", "FUZZ", "AUDIT"];
  const colors = ["#13b981", "#1f9fb4", "#7aa78f", "#9fb8c4"];
  const nodes = Array.from({ length: 38 }, (_, index) => ({
    label: labels[index % labels.length],
    color: colors[index % colors.length],
    x: Math.random(),
    y: Math.random(),
    vx: (Math.random() - 0.5) * 0.0009,
    vy: (Math.random() - 0.5) * 0.0009,
  }));

  function resize() {
    const ratio = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.max(1, Math.floor(rect.width * ratio));
    canvas.height = Math.max(1, Math.floor(rect.height * ratio));
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
  }

  function draw() {
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const scanline = context.createLinearGradient(0, 0, width, height);
    scanline.addColorStop(0, "rgba(19, 185, 129, 0.04)");
    scanline.addColorStop(0.5, "rgba(31, 159, 180, 0.03)");
    scanline.addColorStop(1, "rgba(255, 255, 255, 0.025)");
    context.clearRect(0, 0, width, height);
    context.fillStyle = scanline;
    context.fillRect(0, 0, width, height);
    context.lineWidth = 1;
    context.font = "12px JetBrains Mono, monospace";

    nodes.forEach((node) => {
      node.x += node.vx;
      node.y += node.vy;
      if (node.x < 0.04 || node.x > 0.96) {
        node.vx *= -1;
      }
      if (node.y < 0.08 || node.y > 0.92) {
        node.vy *= -1;
      }
    });

    for (let index = 0; index < nodes.length; index += 1) {
      for (let next = index + 1; next < nodes.length; next += 1) {
        const a = nodes[index];
        const b = nodes[next];
        const ax = a.x * width;
        const ay = a.y * height;
        const bx = b.x * width;
        const by = b.y * height;
        const distance = Math.hypot(ax - bx, ay - by);
        if (distance < 170) {
          context.strokeStyle = `${a.color}${Math.round((0.18 - distance / 980) * 255).toString(16).padStart(2, "0")}`;
          context.beginPath();
          context.moveTo(ax, ay);
          context.lineTo(bx, by);
          context.stroke();
        }
      }
    }

    nodes.forEach((node, index) => {
      const x = node.x * width;
      const y = node.y * height;
      context.shadowColor = node.color;
      context.shadowBlur = 10;
      context.fillStyle = node.color;
      context.fillRect(x - 4, y - 4, 8, 8);
      context.shadowBlur = 0;
      context.fillStyle = "rgba(249, 247, 238, 0.52)";
      context.fillText(node.label, x + 10, y + 4);
    });

    requestAnimationFrame(draw);
  }

  window.addEventListener("resize", resize);
  resize();
  draw();
}

function renderStats(site) {
  elements.statGrid.innerHTML = "";
  [
    ["Years", site.yearsExperience],
    ["Projects", site.projectsCompleted],
    ["Clients", site.happyClients],
  ].forEach(([label, value]) => {
    const card = document.createElement("article");
    card.className = "stat-card";
    card.innerHTML = `<span>${label}</span><strong>${value}</strong>`;
    elements.statGrid.append(card);
  });
}

function renderProjects(projects) {
  elements.projectGrid.innerHTML = "";
  projects.forEach((project, index) => {
    const node = templates.projectCard.content.firstElementChild.cloneNode(true);
    node.querySelector(".project-category").textContent = project.category;
    node.querySelector(".feature-pill").textContent = project.featured ? `0${index + 1} Featured` : `0${index + 1}`;
    node.querySelector(".project-title").textContent = project.title;
    node.querySelector(".project-summary").textContent = project.summary;
    const stackList = node.querySelector(".stack-list");
    stackList.innerHTML = "";
    String(project.stack || "")
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean)
      .forEach((item) => {
        const chip = document.createElement("span");
        chip.textContent = item;
        stackList.append(chip);
      });
    node.querySelector(".project-live").href = project.liveUrl || "#";
    node.querySelector(".project-github").href = project.githubUrl || "#";
    elements.projectGrid.append(node);
  });
}

function renderExperience(experiences) {
  elements.experienceList.innerHTML = "";
  experiences.forEach((item) => {
    const node = templates.timelineItem.content.firstElementChild.cloneNode(true);
    node.querySelector(".timeline-meta").textContent = `${item.startLabel} - ${item.endLabel} | ${item.company}`;
    node.querySelector(".timeline-role").textContent = item.role;
    node.querySelector(".timeline-summary").textContent = item.summary;
    elements.experienceList.append(node);
  });
}

function renderSkills(skills) {
  elements.skillsCloud.innerHTML = "";
  skills.forEach((item, index) => {
    const node = templates.skillChip.content.firstElementChild.cloneNode(true);
    node.querySelector(".skill-category").textContent = `${String(index + 1).padStart(2, "0")} / ${item.category}`;
    node.querySelector(".skill-label").textContent = item.label;
    elements.skillsCloud.append(node);
  });
}

function renderTestimonials(testimonials) {
  elements.testimonialGrid.innerHTML = "";
  testimonials.forEach((item) => {
    const node = templates.testimonial.content.firstElementChild.cloneNode(true);
    node.querySelector(".testimonial-quote").textContent = `"${item.quote}"`;
    node.querySelector(".testimonial-author").textContent = `${item.authorName} | ${item.authorRole}`;
    elements.testimonialGrid.append(node);
  });
}

async function handleContactSubmit(event) {
  event.preventDefault();
  elements.contactFeedback.textContent = "Sending...";
  try {
    await apiFetch("/api/contact", {
      method: "POST",
      body: JSON.stringify({
        name: elements.contactName.value,
        email: elements.contactEmail.value,
        company: elements.contactCompany.value,
        budget: elements.contactBudget.value,
        message: elements.contactMessage.value,
      }),
    });
    elements.contactForm.reset();
    elements.contactFeedback.textContent = "Inquiry received. It is now stored in your dashboard.";
  } catch (error) {
    elements.contactFeedback.textContent = error.message;
  }
}

async function handleAuthSubmit(event) {
  event.preventDefault();
  elements.authFeedback.textContent = state.authMode === "login" ? "Signing in..." : "Creating account...";
  try {
    const response = await apiFetch(state.authMode === "login" ? "/api/login" : "/api/register", {
      method: "POST",
      body: JSON.stringify({
        name: elements.authName.value,
        email: elements.authEmail.value,
        password: elements.authPassword.value,
      }),
    });
    state.session = response.user;
    state.adminData = response.admin || null;
    elements.authFeedback.textContent = "Access granted.";
    elements.authForm.reset();
    renderAdminState();
  } catch (error) {
    elements.authFeedback.textContent = error.message;
  }
}

async function handleLogout() {
  try {
    await apiFetch("/api/logout", { method: "POST", body: JSON.stringify({}) });
    state.session = null;
    state.adminData = null;
    renderAdminState();
  } catch (error) {
    elements.adminFeedback.textContent = error.message;
  }
}

function renderAdminState() {
  const isAdmin = Boolean(state.session?.isAdmin && state.adminData);
  elements.authPanel.classList.toggle("hidden", isAdmin);
  elements.adminPanel.classList.toggle("hidden", !isAdmin);
  elements.authHeading.textContent = isAdmin ? "Admin active" : state.authMode === "login" ? "Sign in" : "Create owner account";
  if (!isAdmin) {
    return;
  }

  elements.adminGreeting.textContent = `${state.session.name} dashboard`;
  const site = state.adminData.site;
  elements.ownerNameInput.value = site.ownerName;
  elements.ownerRoleInput.value = site.ownerRole;
  elements.ownerLocationInput.value = site.ownerLocation;
  elements.heroIntroInput.value = site.heroIntro;
  elements.heroTitleInput.value = site.heroTitle;
  elements.heroBlurbInput.value = site.heroBlurb;
  elements.aboutTitleInput.value = site.aboutTitle;
  elements.aboutBodyInput.value = site.aboutBody;
  elements.primaryCtaLabelInput.value = site.primaryCtaLabel;
  elements.primaryCtaUrlInput.value = site.primaryCtaUrl;
  elements.secondaryCtaLabelInput.value = site.secondaryCtaLabel;
  elements.secondaryCtaUrlInput.value = site.secondaryCtaUrl;
  elements.emailInput.value = site.email;
  elements.phoneInput.value = site.phone;
  elements.githubUrlInput.value = site.githubUrl;
  elements.linkedinUrlInput.value = site.linkedinUrl;
  elements.twitterUrlInput.value = site.twitterUrl;
  elements.resumeUrlInput.value = site.resumeUrl;
  elements.availabilityLabelInput.value = site.availabilityLabel;
  elements.yearsExperienceInput.value = site.yearsExperience;
  elements.projectsCompletedInput.value = site.projectsCompleted;
  elements.happyClientsInput.value = site.happyClients;

  renderEditorCollection("project", state.adminData.projects || []);
  renderEditorCollection("experience", state.adminData.experiences || []);
  renderEditorCollection("skill", state.adminData.skills || []);
  renderEditorCollection("testimonial", state.adminData.testimonials || []);
  renderMessages(state.adminData.messages || []);
  renderDashboardMetrics(state.adminData.summary || {});
}

function renderEditorCollection(type, items) {
  const host = getEditorHost(type);
  host.innerHTML = "";
  items.forEach((item) => host.append(createEditorCard(type, item)));
}

function getEditorHost(type) {
  const map = {
    project: elements.projectEditorList,
    experience: elements.experienceEditorList,
    skill: elements.skillEditorList,
    testimonial: elements.testimonialEditorList,
  };
  return map[type];
}

function addEditorCard(type) {
  const item =
    type === "project"
      ? { id: uid(), title: "", category: "", summary: "", stack: "", githubUrl: "", liveUrl: "", featured: false, sortOrder: 99 }
      : type === "experience"
        ? { id: uid(), role: "", company: "", startLabel: "", endLabel: "", summary: "", sortOrder: 99 }
        : type === "skill"
          ? { id: uid(), label: "", category: "", sortOrder: 99 }
          : { id: uid(), authorName: "", authorRole: "", quote: "", sortOrder: 99 };
  getEditorHost(type).append(createEditorCard(type, item));
}

function createInput(labelText, className, value = "", tag = "input", type = "text") {
  const label = document.createElement("label");
  label.innerHTML = `<span>${labelText}</span>`;
  const input = document.createElement(tag);
  input.className = className;
  if (tag === "input") {
    input.type = type;
  } else {
    input.rows = 4;
  }
  if (type === "checkbox") {
    input.checked = Boolean(value);
  } else {
    input.value = value ?? "";
  }
  label.append(input);
  return label;
}

function createEditorCard(type, item) {
  const card = document.createElement("article");
  card.className = "editor-card";
  card.dataset.type = type;
  card.dataset.id = item.id;

  const row = document.createElement("div");
  row.className = "editor-row";

  if (type === "project") {
    row.append(
      createInput("Title", "field-title", item.title),
      createInput("Category", "field-category", item.category),
      createInput("Summary", "field-summary", item.summary, "textarea"),
      createInput("Stack", "field-stack", item.stack),
    );
    const dual = document.createElement("div");
    dual.className = "editor-row two";
    dual.append(
      createInput("GitHub URL", "field-github", item.githubUrl, "input", "url"),
      createInput("Live URL", "field-live", item.liveUrl, "input", "url"),
    );
    row.append(dual, createInput("Featured", "field-featured", item.featured, "input", "checkbox"), createInput("Sort order", "field-order", item.sortOrder, "input", "number"));
  }

  if (type === "experience") {
    row.append(
      createInput("Role", "field-role", item.role),
      createInput("Company", "field-company", item.company),
    );
    const dual = document.createElement("div");
    dual.className = "editor-row two";
    dual.append(
      createInput("Start label", "field-start", item.startLabel),
      createInput("End label", "field-end", item.endLabel),
    );
    row.append(dual, createInput("Summary", "field-summary", item.summary, "textarea"), createInput("Sort order", "field-order", item.sortOrder, "input", "number"));
  }

  if (type === "skill") {
    const dual = document.createElement("div");
    dual.className = "editor-row two";
    dual.append(
      createInput("Skill label", "field-label", item.label),
      createInput("Category", "field-category", item.category),
    );
    row.append(dual, createInput("Sort order", "field-order", item.sortOrder, "input", "number"));
  }

  if (type === "testimonial") {
    row.append(
      createInput("Author name", "field-author", item.authorName),
      createInput("Author role", "field-author-role", item.authorRole),
      createInput("Quote", "field-quote", item.quote, "textarea"),
      createInput("Sort order", "field-order", item.sortOrder, "input", "number"),
    );
  }

  const actions = document.createElement("div");
  actions.className = "card-actions";
  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "ghost-button";
  remove.textContent = "Remove";
  remove.addEventListener("click", () => card.remove());
  actions.append(remove);

  card.append(row, actions);
  return card;
}

function renderMessages(messages) {
  elements.messageList.innerHTML = "";
  if (!messages.length) {
    elements.messageList.innerHTML = `<article class="message-card"><p class="muted-text">No inquiries yet.</p></article>`;
    return;
  }
  messages.forEach((message) => {
    const card = document.createElement("article");
    card.className = "message-card";
    card.innerHTML = `
      <div class="message-card-header">
        <strong>${message.name}</strong>
        <span class="muted-text">${new Date(message.createdAt).toLocaleString()}</span>
      </div>
      <p class="muted-text">${message.email} | ${message.company || "No company"} | ${message.budget || "No budget specified"}</p>
      <p>${message.message}</p>
    `;
    const actions = document.createElement("div");
    actions.className = "message-card-actions";
    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "ghost-button";
    remove.textContent = "Delete message";
    remove.addEventListener("click", () => deleteMessage(message.id));
    actions.append(remove);
    card.append(actions);
    elements.messageList.append(card);
  });
}

function renderDashboardMetrics(summary) {
  elements.dashboardMetrics.innerHTML = "";
  [
    ["Projects", summary.projects || 0],
    ["Experience", summary.experienceItems || 0],
    ["Skills", summary.skills || 0],
    ["Testimonials", summary.testimonials || 0],
    ["Messages", summary.messages || 0],
  ].forEach(([label, value]) => {
    const node = templates.dashboardMetric.content.firstElementChild.cloneNode(true);
    node.querySelector(".metric-label").textContent = label;
    node.querySelector(".metric-value").textContent = value;
    elements.dashboardMetrics.append(node);
  });
}

function collectSiteSettings() {
  return {
    ownerName: elements.ownerNameInput.value.trim(),
    ownerRole: elements.ownerRoleInput.value.trim(),
    ownerLocation: elements.ownerLocationInput.value.trim(),
    heroIntro: elements.heroIntroInput.value.trim(),
    heroTitle: elements.heroTitleInput.value.trim(),
    heroBlurb: elements.heroBlurbInput.value.trim(),
    aboutTitle: elements.aboutTitleInput.value.trim(),
    aboutBody: elements.aboutBodyInput.value.trim(),
    primaryCtaLabel: elements.primaryCtaLabelInput.value.trim(),
    primaryCtaUrl: elements.primaryCtaUrlInput.value.trim(),
    secondaryCtaLabel: elements.secondaryCtaLabelInput.value.trim(),
    secondaryCtaUrl: elements.secondaryCtaUrlInput.value.trim(),
    email: elements.emailInput.value.trim(),
    phone: elements.phoneInput.value.trim(),
    githubUrl: elements.githubUrlInput.value.trim(),
    linkedinUrl: elements.linkedinUrlInput.value.trim(),
    twitterUrl: elements.twitterUrlInput.value.trim(),
    resumeUrl: elements.resumeUrlInput.value.trim(),
    availabilityLabel: elements.availabilityLabelInput.value.trim(),
    yearsExperience: Number(elements.yearsExperienceInput.value || 0),
    projectsCompleted: Number(elements.projectsCompletedInput.value || 0),
    happyClients: Number(elements.happyClientsInput.value || 0),
  };
}

function collectCards(type) {
  return Array.from(getEditorHost(type).querySelectorAll(".editor-card")).map((card) => {
    const base = { id: card.dataset.id, sortOrder: Number(card.querySelector(".field-order")?.value || 0) };
    if (type === "project") {
      return {
        ...base,
        title: card.querySelector(".field-title").value.trim(),
        category: card.querySelector(".field-category").value.trim(),
        summary: card.querySelector(".field-summary").value.trim(),
        stack: card.querySelector(".field-stack").value.trim(),
        githubUrl: card.querySelector(".field-github").value.trim(),
        liveUrl: card.querySelector(".field-live").value.trim(),
        featured: card.querySelector(".field-featured").checked,
      };
    }
    if (type === "experience") {
      return {
        ...base,
        role: card.querySelector(".field-role").value.trim(),
        company: card.querySelector(".field-company").value.trim(),
        startLabel: card.querySelector(".field-start").value.trim(),
        endLabel: card.querySelector(".field-end").value.trim(),
        summary: card.querySelector(".field-summary").value.trim(),
      };
    }
    if (type === "skill") {
      return {
        ...base,
        label: card.querySelector(".field-label").value.trim(),
        category: card.querySelector(".field-category").value.trim(),
      };
    }
    return {
      ...base,
      authorName: card.querySelector(".field-author").value.trim(),
      authorRole: card.querySelector(".field-author-role").value.trim(),
      quote: card.querySelector(".field-quote").value.trim(),
    };
  });
}

async function saveAdminContent() {
  elements.adminFeedback.textContent = "Saving...";
  try {
    const response = await apiFetch("/api/admin/site", {
      method: "POST",
      body: JSON.stringify({
        site: collectSiteSettings(),
        projects: collectCards("project"),
        experiences: collectCards("experience"),
        skills: collectCards("skill"),
        testimonials: collectCards("testimonial"),
      }),
    });
    state.adminData = response;
    state.publicData = {
      site: response.site,
      projects: response.projects,
      experiences: response.experiences,
      skills: response.skills,
      testimonials: response.testimonials,
    };
    renderPublic();
    renderAdminState();
    elements.adminFeedback.textContent = "Saved. Your public portfolio just updated.";
  } catch (error) {
    elements.adminFeedback.textContent = error.message;
  }
}

async function deleteMessage(id) {
  elements.adminFeedback.textContent = "Deleting message...";
  try {
    const response = await apiFetch("/api/admin/messages/delete", {
      method: "POST",
      body: JSON.stringify({ id }),
    });
    state.adminData = response;
    state.publicData = {
      site: response.site,
      projects: response.projects,
      experiences: response.experiences,
      skills: response.skills,
      testimonials: response.testimonials,
    };
    renderAdminState();
    elements.adminFeedback.textContent = "Message deleted.";
  } catch (error) {
    elements.adminFeedback.textContent = error.message;
  }
}

bootstrap().catch((error) => {
  console.error(error);
});
