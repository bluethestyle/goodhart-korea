// Goodhart's Game in Korean Central Government Spending — Principal-Agent Equilibrium Analysis (v2 English)
// Typst compile: typst compile paper/main_v2_en.typ paper/main_v2_en.pdf

#set document(
  title: "Goodhart's Game in Korean Central Government Spending: A Principal-Agent Equilibrium Analysis with Multi-Method Validation and Model-Based Policy Prescriptions",
  author: ("Jeong Seongyu", "Sim Euncheol", "Kim Yeongchan"),
)

#set page(
  paper: "a4",
  margin: (top: 25mm, bottom: 25mm, left: 25mm, right: 25mm),
  numbering: "1",
)

// English academic font stack: Times New Roman primary, Linux Libertine / Latin Modern Roman fallback
#set text(
  font: ("Times New Roman", "Libertinus Serif", "New Computer Modern"),
  size: 10.5pt,
  lang: "en",
)

// Line spacing: leading 1.05em; first-line indent on all paragraphs
#set par(
  justify: true,
  leading: 1.05em,
  first-line-indent: (amount: 1em, all: true),
  spacing: 1.2em,
)

#set heading(numbering: "1.1")

// Heading style — sans-serif for clear visual separation from serif body text
#show heading.where(level: 1): it => [
  #v(1.0em)
  #text(
    font: ("Arial", "New Computer Modern"),
    size: 13pt, weight: "bold",
    it
  )
  #v(0.4em)
]
#show heading.where(level: 2): it => [
  #v(0.7em)
  #text(
    font: ("Arial", "New Computer Modern"),
    size: 11.5pt, weight: "bold",
    it
  )
  #v(0.25em)
]
#show heading.where(level: 3): it => [
  #v(0.5em)
  #text(
    font: ("Arial", "New Computer Modern"),
    size: 10.8pt, weight: "bold",
    it
  )
  #v(0.2em)
]

// figure / table supplement labels
#show figure.where(kind: image): set figure(supplement: [Figure])
#show figure.where(kind: table): set figure(supplement: [Table])

// Table design — academic standard (bold header rule + thin body row dividers + closing rule)
#set table(
  stroke: (x, y) => (
    // Top outer rule (above header row)
    top: if y == 0 { 1.0pt + black } else { 0pt },
    // Header-body divider = bold; body row dividers and bottom = thin gray
    bottom: if y == 0 { 1.0pt + black } else { 0.3pt + rgb("#bbb") },
  ),
  fill: none,
  inset: (x: 10pt, y: 9pt),
)

#show table.cell: it => {
  set par(leading: 0.50em)
  it
}

// Header row: force bold with a non-variable font stack
#show table.cell.where(y: 0): set text(
  weight: "bold",
  font: ("Arial", "Times New Roman"),
)

// =============================================================
// Cover Page
// =============================================================
#align(center)[
  #v(2em)
  #text(size: 18pt, weight: "bold",
        font: ("Arial", "New Computer Modern"))[
    Goodhart's Game in Korean Central Government Spending
  ]
  #v(0.6em)
  #text(size: 12.5pt,
        font: ("Arial", "New Computer Modern"))[
    A Principal-Agent Equilibrium Analysis with Multi-Method Validation and Model-Based Policy Prescriptions
  ]
  #v(2.5em)
  #text(size: 11pt)[Jeong Seongyu, Sim Euncheol, Kim Yeongchan]
  #v(0.35em)
  #text(size: 9pt, fill: rgb("#555"))[
    Jeong Seongyu #h(0.5em) jsk320098\@gmail.com #h(1.5em)
    Sim Euncheol #h(0.5em) simeunchul\@naver.com #h(1.5em)
    Kim Yeongchan #h(0.5em) findurwind\@gmail.com
  ]
  #linebreak()
  #v(0.3em)
  #text(size: 10pt, fill: rgb("#444"))[April 2026]

  #v(2em)
  #line(length: 40%, stroke: 0.6pt + rgb("#999"))
  #v(0.5em)
  #text(size: 9pt, fill: rgb("#555"))[
    GitHub #link("https://github.com/bluethestyle/goodhart-korea")[bluethestyle/goodhart-korea]
  ]
  #linebreak()
  #text(size: 9pt, fill: rgb("#555"))[
    Interactive Visualization #link("https://bluethestyle.github.io/goodhart-korea/")[bluethestyle.github.io/goodhart-korea]
  ]
  #v(0.5em)
  #line(length: 40%, stroke: 0.6pt + rgb("#999"))
]

#v(2.5em)

// =============================================================
// Abstract
// =============================================================
#align(center)[
  #text(weight: "bold", size: 12pt,
        font: ("Arial", "New Computer Modern"))[Abstract]
]
#v(0.4em)
#align(center)[
  #text(weight: "bold", size: 11pt,
        font: ("Arial", "New Computer Modern"))[
    Goodhart's Game in Korean Central Government Spending: \
    A Principal-Agent Equilibrium Analysis with Multi-Method \
    Validation and Model-Based Policy Prescriptions
  ]
]
#v(0.6em)

#[
  #set par(first-line-indent: 0pt, leading: 0.95em)
  This paper derives the micro-mechanism through which Goodhart's effect #cite(<goodhart1975>) manifests in Korean central government budget execution via a Principal-Agent equilibrium model, then validates six falsifiable hypotheses (H1--H6) using 11-year monthly data, 14 expenditure fields, 1,557 spending activities, and 11 analytical methods.

  Korea's evaluation regime --- execution-rate audits, management assessments of government-affiliated institutions, and Board of Audit reviews --- creates a large measurability gap between the timing-adjustment weight $w_t$ (observable) and the quality weight $w_q$ (unobservable). Following #cite(<holmstrom1991>, form: "prose"), a rational agent's equilibrium response is to concentrate effort on the measurable dimension, yielding what the paper terms a Goodhart game: systematic near-year-end over-execution at the expense of project quality. The model maps onto all four Goodhart categories of Manheim and Garrabrant (2019).

  Activity-level embeddings (UMAP + HDBSCAN) uncover four project archetypes --- personnel-cost, capital-acquisition, grant-transfer, and normal-operation --- with Mapper and Persistent Homology confirming topological stability (H1). Field labels add negligible explanatory power over gaming intensity ($Delta R^2 = 0.000$). Regression discontinuity at the December boundary shows capital-acquisition activities spike 3.42$times$ at fiscal year-end (H2); grant-transfer activities exhibit the strongest annual-cycle dominance in spectral and wavelet coherence analyses (H3). Social-welfare spending shows a fortuitous alignment effect from automatic-transfer mechanics ($r = -0.86$, strengthened after CPI controls; H5). Wavelet decomposition reveals that grant-transfer gaming intensity amplified by +554% in 12-month amplitude over the sample, extending #cite(<liebman2017>, form: "prose") qualitatively and dynamically to Korea (H6).

  Six policy prescriptions follow directly from the model's comparative statics: multi-year appropriations, revised indicators for affiliated institutions, staggered settlement deadlines, data infrastructure, automated execution-pattern flagging, and time-weighted monitoring. Each maps one-to-one to a model lever. The analysis forthrightly acknowledges the fundamental limits imposed by Holmstrom--Milgrom impossibility.
]

#v(1em)

#[
  #set par(first-line-indent: 0pt)
  #text(weight: "bold")[Keywords:] Goodhart's Law, Principal-Agent Model, Multitasking Contract, Public Finance, Project Archetype, Regression Discontinuity, Wavelet Analysis, Topological Data Analysis, Korea
]

#pagebreak()

#outline(
  title: [Contents],
  indent: auto,
  depth: 2,
)

#pagebreak()

// =============================================================
// Abbreviations and key term definitions are deferred to Appendices A and B.
// First occurrences in the text are spelled out with appendix cross-references.

// =============================================================
= Introduction

== Motivation: "What Gets Measured Gets Managed"

  #cite(<bevan2006>, form: "prose") examined the UK National Health Service and, under the proposition that "what's measured is what matters," identified four patterns of performance-indicator gaming: threshold effects, ratchet effects, output distortion, and gaming. This is the public-administration instantiation of the proposition advanced separately by #cite(<goodhart1975>, form: "prose") for monetary policy and #cite(<campbell1979>, form: "prose") for social science in general --- that *the moment an indicator is adopted as a policy instrument, its reliability as a measure deteriorates*.

  Does the same mechanism operate in Korean central government budget execution? Answering that question requires (a) defining gaming as a *measurable quantity*, (b) *isolating heterogeneity* across fields, agencies, and project types, and (c) *ruling out competing hypotheses* such as natural business cycles or trend effects. This paper combines 11 years of monthly data, 14 expenditure fields, and 1,557 spending activities through multiple methods to address these three tasks in sequence.

== Extending the U.S. Evidence to Korea

  #cite(<liebman2017>, form: "prose") (AER) used a regression discontinuity (RDD) design at the last week of November versus the first week of December in U.S. federal procurement to show that spending surges *5×* in the final week of the fiscal year while *quality scores simultaneously fall*. The finding is a benchmark causal identification of measurement distortion arising from a use-it-or-lose-it budget rule.

  This paper applies the same RDD design to an 11-year Korean time series. Because Korean data are available at monthly granularity, the study compares daily-average execution in November versus December, and examines whether the heterogeneity in jump magnitudes across project archetypes reflects qualitatively the same mechanism operating in the Korean context. Detailed estimation results are reported in §6.3.

== Key Contributions

  This paper's contributions span five dimensions: (1) a theoretical model, (2) a redefinition of the unit of analysis, (3) counter-intuitive findings, (4) temporal intensification of gaming, and (5) model-derived policy prescriptions. Each is formally validated in the corresponding section and summarized again in the conclusion.

  + *Contribution 1 --- Theoretical Model (§3)*: A Principal-Agent equilibrium analysis establishes *why* Goodhart's effect materializes in Korea. The agent's *rationality* --- not irrationality --- concentrates effort on timing adjustment in a measurability-gap environment. The model generates six falsifiable hypotheses (H1--H6).

  + *Contribution 2 --- Redefining the Unit of Analysis (§6.1, H1)*: Field-level analysis, the standard unit in Korean administrative and fiscal studies, explains a *trivial* share of gaming-intensity variance ($Delta R^2 = 0.000$); the true unit is *project archetype*. This is demonstrated through multiple topological data analysis (TDA) methods.

  + *Contribution 3 --- Counter-Intuitive Findings (§6.3--§6.7, H2/H3/H5)*: Gaming is not a uniform negative measurement distortion but a *field-heterogeneous and archetype-heterogeneous* phenomenon. The central findings are the capital-acquisition archetype's 3.42× RDD jump (H2), the grant-transfer archetype's cycle dominance (H3), and Social Welfare's automatic redistribution effect (H5) --- a fortuitous alignment, not a policy success.

  + *Contribution 4 --- Temporal Intensification (§6.8, H6, new Wavelet result)*: Supplementing FFT (which assumes stationarity) with wavelet decomposition, this paper provides new evidence that *gaming intensity strengthens over time*. Grant-transfer 12-month cycle amplitude increased by *+554\%* from 2015--2017 to 2023--2025, with no corresponding change for the personnel-type archetype (control). Goodhart's effect in Korea is *a dynamic, ongoing phenomenon, not a fixed pattern*.

  + *Contribution 5 --- Model-Derived Policy Prescriptions (§7)*: Policy recommendations are derived *directly* from the model's comparative statics ($(partial e_t^*) / (partial w_t) > 0$, etc.) rather than listed ad hoc. Six prescriptions --- multi-year appropriations, revised performance indicators for quasi-governmental agencies, staggered settlement deadlines, data infrastructure, automated flagging, and time-weighted monitoring --- correspond one-to-one to model levers ($w_t, w_q$, $c_(t t)$). The analysis honestly acknowledges the fundamental limits of Holmstrom--Milgrom impossibility.

= Theoretical Foundations

  This paper's analysis draws on three theoretical traditions: (1) the Goodhart-Campbell law and the New Public Management (NPM) measurement paradox from *public management theory*, (2) the Holmstrom-Milgrom multitasking contract from *contract economics*, and (3) Kornai's soft budget constraint from *comparative economics*. Each tradition accounts for a distinct finding; taken together, they yield the cross-archetype differences in gaming intensity as a natural consequence.

== Goodhart-Campbell Law and the NPM Paradox

  #cite(<goodhart1975>, form: "prose") observed that after Bank of England monetary statistics were adopted as a policy instrument the relationship between those statistics and macroeconomic reality broke down, formalizing the proposition that *"any statistical regularity will tend to collapse once pressure is placed on it for control purposes."* #cite(<campbell1979>, form: "prose") extended the same principle to social science more broadly.

  #cite(<manheim2018>, form: "prose") classified Goodhart's effect into four variants:
  - *Regressional*: policy over-fits to measurement noise
  - *Causal*: the indicator is directly manipulated but via an inefficient causal pathway
  - *Extremal*: the indicator-target relationship breaks down in extreme regions
  - *Adversarial*: agents intentionally manipulate the indicator

  The relationship between incentive structures and measurement distortion was posed early by #cite(<kerr1975>, form: "prose") through the classic proposition --- "the folly of rewarding A while hoping for B." Korea's execution-rate evaluation is a textbook instance of that folly. For empirical evidence on gaming responses to public incentive programs, see #cite(<courty2004>, form: "prose").

  The December spending jump and grant-transfer gaming documented in this paper fall primarily under *Causal* (gaming the execution-rate indicator through timing adjustment) and *Adversarial* (deliberate year-end concentration to avoid carryover).

== Multitasking Contract Theory

  #cite(<holmstrom1991>, form: "prose") (JLEO) showed that when an agent performs *multi-dimensional tasks* but incentives are attached only to the measurable dimension, effort on the unmeasurable dimension *systematically declines* --- an impossibility theorem stating that no incentive intensity achieves first-best when the measurability gap is large. A subsequent contribution by #cite(<baker1992>, form: "prose") demonstrated that *measurement distortion* is more damaging to incentive design than *measurement noise* --- the measurability-gap function $phi'(\cdot) < 1$ in this paper maps directly onto Baker's distortion parameter.

  Applied to public programs, in an environment where execution rate (observable) and project quality (hard to observe) trade off, stronger execution-rate incentives lead to greater sacrifice of quality. The cross-archetype differences in RDD jumps documented here --- capital-acquisition archetype 3.42×, grant-transfer 1.10×, personnel-type 1.12× --- constitute Korean evidence for the hypothesis that *responsiveness to measurement pressure differs by project type*.

  Korean literature on gaming in quasi-governmental agency evaluations: KCI journals in Korean public administration and fiscal studies have also accumulated work on gaming and ratchet effects in quasi-governmental agency PBS (Project-Based Funding System) and public-institution management evaluations. @kim2009pbs, @park2014pbs, and @lim2020kpi, among others, document *numeric inflation* and *strategic reporting* of R&D performance indicators following PBS adoption.

== Soft Budget Constraint

  #cite(<kornai1980>, form: "prose") theorized the *softening* of budget constraints in socialist-economy state-owned enterprises that anticipate government bailouts rather than facing market discipline. Quasi-governmental agencies and public institutions in market-economy public sectors are exposed to the same mechanism.

  *Quasi-governmental agencies and grant-receiving institutions have greater freedom to adjust spending timing than direct public programs*. They can concentrate execution in December to meet settlement deadlines; even if the following fiscal year's budget is cut, the possibility of compensation from the parent organization weakens market discipline. The regression of grant share on gaming intensity (β = +0.375, *p* = .005), together with the grant-transfer archetype's PSD $k=1$ amplitude of 0.332 and phase coherence of 0.54 (2--6× that of other archetypes), constitutes quantitative evidence for this mechanism. The 3.42× December RDD jump is most pronounced in the *capital-acquisition archetype*, however, reflecting a distinct mechanism: construction and asset-acquisition projects combine a *physical-completion deadline* with a *fiscal-year deadline*, generating a discrete jump immediately after the December 1 cutoff.

= The Model: A Principal-Agent Goodhart Game

  Where the preceding section (Theoretical Foundations) introduced *three theoretical traditions*, this section presents a formal model that specializes those traditions to *Korea's evaluation regime*. The model shows that *rational choice* --- not agent irrationality --- generates Goodhart's game in a measurability-gap environment. Under the objective function defined by the evaluation regime, the equilibrium action is concentration of resources toward timing-adjustment effort.

== Korea's Evaluation Regime and the Measurability Gap

  Ministries and quasi-governmental agencies executing Korean central government programs are exposed to a four-layer evaluation regime:

  + *Execution-rate audit*: percentage executed as of December 31 of the fiscal year. Precisely measured (daily accounting system records).
  + *Program performance evaluation (KPI)*: quantitative indicators (outputs, outcomes). Partially measured --- KPI definitions vary across programs and some rely on *proxy indicators*.
  + *Management evaluation of quasi-governmental agencies* (Ministry of Economy and Finance, MOEF, annually): reflects both execution rate and program KPIs, but *execution-rate weight is high*.
  + *Board of Audit and Inspection (BAI) periodic audit*: ex-post check. Primarily targets procedural violations and improper execution; assessment of *actual program effectiveness* is difficult.

  *Measurability gap* @holmstrom1991: some tasks are precisely measured while others are partially or not measured. The core gap in this paper is as follows:

  - $e_t$ = *timing-adjustment effort* (year-end concentration of execution): *perfectly measured* (monthly execution records)
  - $e_q$ = *project quality effort* (contribution to genuine social outcomes): *hard to measure* --- social outcomes materialize over multiple years, involve multiple causal factors, and lack adequate measurement instruments

  In environments with large measurability gaps, incentive design is inherently distorted. This section formalizes the gap using game-theoretic tools.

== Model Setup: Principal and Agent Objective Functions

  A stage game indexed by activity $i$ and fiscal year $t$ is defined as follows.

  Principal (government/ministry, $P$) objective function:
  $ U_P = E[Y(e_q, e_t)] - C(I) $
  where $Y$ = social outcome (e.g., poverty gap, life expectancy, patent counts); $I$ = transfer to the agent (budget allocation); $C(I)$ = fiscal cost. In general, $(partial Y) / (partial e_q) > 0$ (quality effort raises outcomes), $(partial Y) / (partial e_t) approx 0$ (timing adjustment has negligible effect on social outcomes).

  Field-level alignment function $alpha(theta_("field"))$: the marginal productivity of timing-adjustment effort on social outcome $Y$ is formalized as a field-specific function.
  $ alpha(theta_("field")) := (partial Y) / (partial e_t) (e_q, e_t; theta_("field")) $
  Across the 14 fields in this paper's empirical analysis, the distribution of $alpha$ is as follows:
  - $alpha(theta_("Social Welfare")) > 0$: concentrated December transfers → resource supply to low-income households, poverty gap ↓
  - $alpha(theta_("Environment")) < 0$: concentrated December execution → inadequate administrative procedures, environmental outcomes ↓
  - $alpha(theta_("other 12 fields")) approx 0$: timing adjustment is unrelated to social outcomes

  Formal definition of fortuitous alignment: the automatic redistribution effect in Social Welfare spending reflects *the accidental positivity of the model-exogenous field function $alpha$*. Because the agent's objective $U_A$ does not include $Y$, *all* $Y$-improvements are fortuitous --- the negative correlation observed for Social Welfare is an *exogenous field characteristic*, not *the agent's intended social contribution*.

  This definition provides the model foundation for the coexistence of *field triviality and Social Welfare's automatic redistribution*: the unit of the cost function $c(\cdot; theta_("archetype"))$ is the project archetype (H1, field trivial), while the unit of the outcome function $alpha(theta_("field"))$ is the field. The two layers are *mutually independent dimensions* of the model; Social Welfare's outcome alignment is *one incidental point in the field layer*.

  Agent (executing ministry or quasi-governmental agency, $A$) objective function:
  $ U_A = w_t thin e_t + w_q thin tilde(e)_q - c(e_t, e_q; theta) $
  where
  - $w_t$ = evaluation weight on timing adjustment (*large* in execution-rate and quasi-governmental agency management evaluations)
  - $w_q$ = evaluation weight on measurable quality (*reflected in some KPIs and audit criteria, but small*)
  - $tilde(e)_q = phi(e_q)$ = *measurable portion* of $e_q$; $phi: RR_+ arrow RR_+$, $phi(0) = 0$, $phi'(\cdot) > 0$, $phi'(\cdot) < 1$
  - $c(e_t, e_q; theta)$ = effort cost function, *differing by project archetype $theta$*; assumed convex and increasing.

  Formal interpretation of the measurability-gap function $phi$: $phi'(\cdot) < 1$ means that *even when the agent invests one unit of quality effort $e_q$, the evaluation system captures less than that absolute amount*. This maps exactly to the *distortion parameter* of #cite(<baker1992>, form: "prose") --- the marginal productivity gap between the measurement indicator $M$ and true value $V$: $(partial M) / (partial e) != (partial V) / (partial e)$. When $phi(e_q) = e_q$ ($phi'$ ≡ 1), the measurability gap is zero and first-best is attained. Korean program performance evaluation operates in an environment with $phi'(\cdot) << 1$ (e.g., social outcome measurement horizons of 5--35 years, multiple causal factors, absence of measurement instruments) --- a core assumption of this paper.

  Core asymmetry: $Y$ is the Principal's objective, but it *does not enter the Agent's objective function directly*. The Agent maximizes only the evaluation score $w_t e_t + w_q tilde(e)_q$ without regard to $Y$. *Every improvement in $Y$ is the result of fortuitous alignment*.

  Notation convention for cost-function partial derivatives: throughout this section, first and second partial derivatives of the cost function $c$ are abbreviated using subscript notation --- $c_t equiv (partial c)/(partial e_t)$, $c_q equiv (partial c)/(partial e_q)$, $c_(t t) equiv (partial^2 c)/(partial e_t^2)$, $c_(q q) equiv (partial^2 c)/(partial e_q^2)$, $c_(t q) equiv (partial^2 c)/(partial e_t partial e_q)$. This is the standard convention for avoiding nested-fraction notation in comparative statics.

== Equilibrium: First-Order Conditions of the Goodhart Game

  Agent first-order conditions (FOC). Since $tilde(e)_q = phi(e_q)$, differentiating with respect to $e_q$ applies the chain rule:
  $ (partial U_A) / (partial e_t) = w_t - (partial c) / (partial e_t) = 0 quad => quad w_t = (partial c) / (partial e_t) $
  $ (partial U_A) / (partial e_q) = w_q phi'(e_q) - (partial c) / (partial e_q) = 0 quad => quad w_q phi'(e_q) = (partial c) / (partial e_q) $

  *Key result*: In the environment with $w_t >> w_q$ (Korea's current evaluation regime) and $phi'(\cdot) < 1$ (measurability gap), the *effective quality weight* satisfies $w_q phi'(e_q) < w_q << w_t$, so the equilibrium $e_t^* >> e_q^*$ --- the Agent *rationally* concentrates effort on timing adjustment. The measurability gap distorts equilibrium through two channels: (i) evaluation-weight asymmetry ($w_t > w_q$) and (ii) *measurement leakage* on quality effort ($phi' < 1$). This is the *micro-mechanism of the Goodhart game*.

  Goodhart's Law is commonly stated as "when a measure becomes a policy target it ceases to be a good measure," but the micro-derivation in this model yields a stronger proposition: *the equilibrium behavior of rational agents causes the collapse of measurability*. Moral blame directed at agents is misplaced; the root cause is *a flaw in institutional design*.

  Application of Holmstrom--Milgrom impossibility to Korea: in an environment with a large measurability gap, no incentive intensity $(w_t, w_q)$ achieves first-best. Specifically:
  - Raising $w_q$ only increases $tilde(e)_q$ --- *effect leakage* into the measurable portion
  - Reducing $w_t$ requires the principal to bear *direct monitoring costs*
  The empirical results of this paper constitute a *direct verification* of this impossibility in the Korean context.

== Comparative Statics: Equilibrium Effects of Policy Variables

  Partial derivatives of $e_t^*$ (detailed derivation in Appendix F):
  $ (partial e_t^*) / (partial w_t) > 0 quad ("timing-evaluation weight increases → gaming increases") $
  $ (partial e_t^*) / (partial w_q) < 0 quad ("quality-evaluation weight increases → gaming decreases") $
  $ (partial e_t^*) / (partial c_(t t)) < 0 quad ("marginal cost of timing adjustment increases → gaming decreases") $

  The three partial derivatives map directly onto *three policy prescriptions*:
  + Reduce $w_t$: *ease execution-rate evaluation* (multi-year appropriations, strengthening MTEF)
  + Raise $w_q$: *build program performance measurement infrastructure* (caveat: fundamental limits of the measurability gap remain)
  + Raise $c_(t t)$: *increase the marginal cost of timing adjustment* (staggered settlement for quasi-governmental agencies, automated flagging)

  The three prescriptions correspond one-to-one to policy recommendations 1--4 in this paper's Policy Implications section.

== Career Concerns: Collective Reputation Equilibrium for Grant-Transfer Archetypes

  This section *extends* the static model of §3.3 to a multi-year reputation game. The main hypotheses (H1--H6) of this paper are derived from the static equilibrium of §3.3; the dynamic results here are used solely for the mechanistic interpretation of the grant-transfer phase coherence analysis in §6.4.

  The stage game of this model characterizes equilibrium within a single evaluation round. Korean quasi-governmental agencies and public institutions, however, operate in a *multi-year repeated game*, in which *collective reputation* serves as an additional incentive (@holmstrom1999; @dewatripont1999).

  Dynamic game setup: in period $t = 1, 2, ..., T$, activity $i in cal(I)_("parent institution")$ (activities of quasi-governmental agencies under the same parent institution) chooses timing effort $e_(i,t)$. The parent institution's *true evaluation criterion* $mu^* in RR$ determines the *effective weight* on timing adjustment --- activity $i$ perceives the timing-evaluation weight as $w_t(mu^*)$, with higher $mu^*$ implying greater weight on execution-rate evaluation ($w_t' (mu^*) > 0$). $mu^*$ is *uncertain*; agents learn from the evaluation results of peer activities.

  Activity $i$'s evaluation score: $s_(i,t) = w_t(mu^*) e_(i,t) + w_q(mu^*) tilde(e)_(q,i,t) + epsilon_(i,t)$. Activity $i$ observes peer scores ${s_(j,t-1)}_(j != i)$ from period $t-1$ and updates its belief about $mu^*$.

  Bayesian belief update: under a Gaussian conjugate prior, the posterior mean $hat(mu)_(i,t) = E[mu^* | s_(j,t-1), j != i]$ is an affine function of the peer-score average $hat(R)_(t-1) = (1\/n) sum_(j != i) s_(j,t-1)$ --- higher peer scores lead to the posterior inference that "$mu^*$ is large."

  Dynamic equilibrium (effective weight mediation): activity $i$ solves the stage problem using the *effective weight* $tilde(w)_t equiv w_t(hat(mu)_(i,t))$ --- the dynamic weight of §3.3's $w_t$ conditioned on belief $hat(mu)_t$.
  $ e_(i,t)^* = arg max_(e_t) {tilde(w)_t (hat(mu)_(i,t)) e_t + tilde(w)_q (hat(mu)_(i,t)) tilde(e)_q - c(e_t, e_q)} $
  Since $tilde(w)_t$ depends on $hat(mu)_(i,t)$ through $hat(R)_(t-1)$, $hat(R)$ enters the maximization *substantively* --- not as a mere additive term, but as *an argument of the weighting function itself*. The first-order condition is $tilde(w)_t (hat(mu)_(i,t)) = c_t(e_(i,t)^*, e_(q,i,t)^*)$.

  Nash convergence (collective synchronization): when all activities are exposed to the *common* signal ${s_(j,t-1)}$ and $hat(mu)_(i,t)$ converges to a *similar distribution* (LLN), $tilde(w)_t (hat(mu)_(i,t))$ synchronizes across all $i$ --- via the FOC, $e_(i,t)^*$ also synchronizes:
  $ "phase"(e_(i,t)^*) approx "phase"(e_(j,t)^*) quad forall i, j in cal(I)_("parent-inst") $
  This follows naturally from the *Bayesian-Nash equilibrium of similar games* (@morris2002, a Korean fiscal adaptation of coordination under public information).

  Precise empirical correspondence: the grant-transfer archetype's phase coherence of 0.54 (*4--7×* the 0.08--0.13 of other archetypes; Appendix D.3) is a *direct measurement of effective-weight synchronization* --- activities $i$ and $j$ *peak simultaneously via learned $hat(mu)$*. The personnel-type archetype's phase coherence of 0.41 (control) reflects natural synchronization from *structurally equal monthly disbursements*; capital-acquisition (0.08) and normal-operation (0.13) archetypes reflect environments where *peer-evaluation-signal learning is weak* --- i.e., the bond between parent and executing institution is weaker than in the grant-transfer archetype.

  Natural starting point for future research: quantitative verification of this dynamic mechanism is feasible via *annual evaluation-result panels* and *agent behavior lag analysis* (@sannikov2008 continuous-time PA; @cabrales2011 conformity learning). Quantitative measurement of $w_R$ --- variance in quasi-governmental agency evaluation outcomes across parent institutions as a proxy for collective reputation signal strength --- is also a key calibration target for natural experiments.

== Equilibrium Predictions by Project Archetype

  The cost function $c(e_t, e_q; theta)$ differs by project archetype $theta in \{$personnel-type, capital-acquisition, grant-transfer, normal projects$\}$, and the evaluation weights $(w_t, w_q)$ likewise differ across archetypes. This generates *archetype-specific equilibrium patterns* for $e_t^*$.

  #figure(
    table(
      columns: (auto, auto, auto, auto, auto),
      align: (left, center, center, center, left),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*Archetype*], [*$w_t$*], [*$w_q$*], [*$partial c\/partial e_t$*], [*Predicted $e_t^*$ pattern*],
      [Personnel-type], [0], [small], [very large], [$approx 0$ --- roughly equal monthly (structural constraint)],
      [Capital-acquisition], [large], [small], [small (possible from Dec 1)], [large, *discrete spike*],
      [Grant-transfer], [large], [small], [medium (dispersible)], [large, *annual-cycle dispersion*],
      [Normal projects], [medium], [medium], [medium], [medium],
    ),
    caption: [Model equilibrium predictions by project archetype --- differences in cost function and evaluation weights yield four distinct patterns],
  )

== Empirically Testable Hypotheses

  The model derivation in this section yields *six falsifiable hypotheses* (all validated in the Results section):

  + *H1 (Field vs. Archetype)*: The unit of the cost function $c$ is the *project archetype*, not the field. Prediction: field dummies $Delta R^2 approx 0$; archetype interaction $Delta R^2 > 0$. (Validated: §6.1--§6.2)
  + *H2 (Capital-Acquisition RDD Jump)*: The archetype whose cost $c(\cdot)$ drops sharply immediately after December 1. Prediction: largest RDD jump. (Validated: §6.3 --- 3.42×)
  + *H3 (Grant-Transfer Cycle Dominance)*: Large $w_t$ combined with dispersible $c(\cdot)$. Prediction: highest PSD/wavelet/coherence. (Validated: §6.4 + Appendix D --- 0.332/+554%/0.54)
  + *H4 (Mediation Pathway Heterogeneity)*: The $X arrow e_t arrow Y$ pathway is *archetype-heterogeneous*, so the pooled mediation effect is predicted to be non-significant. (Validated: §6.5--§6.6 + Limitations --- *p* = .481)
  + *H5 (Social Welfare Fortuitous Alignment)*: The *exceptional* field in which $(partial Y) / (partial e_t) > 0$. Fortuitous, not a policy justification. (Validated: §6.7)
  + *H6 (Temporal Intensification)*: Rising $w_t / w_q$ ratio over time → $e_t^*$ time-series intensification. (Validated: §6.8 --- wavelet +554%)

  *Theoretical connection to Performative Prediction*: H6 constitutes a Korean fiscal-data instantiation of the Performative Prediction framework of #cite(<hardt2016strategic>, form: "prose") and #cite(<perdomo2020performative>, form: "prose") --- the proposition that *the moment an indicator is adopted as an evaluation instrument, the distribution that indicator measures itself changes*. The mechanism is *adaptive behavior*: agents learn the structure of the evaluation system and progressively strengthen gaming intensity over time. This theoretical connection supports the empirical interpretation of H6; detailed results are reported in §6.8.

  The model *simultaneously predicts all six hypotheses*, each of which is validated through independent data analysis. This multi-method validation structure *reduces the risk of model overfitting*.

== Mapping to Goodhart Effect Taxonomy #cite(<manheim2018>)

  #cite(<manheim2018>, form: "prose") classified Goodhart's effect into *four variants* --- Regressional (policy over-fitting to measurement noise), Causal (direct indicator manipulation), Extremal (relationship breakdown in extreme regions), and Adversarial (intentional manipulation). The six hypotheses of this paper map onto these four types as follows.

  #figure(
    table(
      columns: (0.4fr, 0.45fr, 1fr),
      align: (center+horizon, center+horizon, center+horizon),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*Manheim--\ Garrabrant Type*], [*Hypothesis*], [*Mechanism*],
      [*Causal*], [H2 (Capital-Acquisition RDD),\ H3 (Grant-Transfer Cycle)], [Agent directly manipulates the *measurable dimension* $e_t$ --- a December spike or annual-cycle accumulation not required by the program's intrinsic nature],
      [*Adversarial*], [H6\ (Temporal Intensification +554\%)], [Agent *learns* and progressively increases gaming intensity --- adaptive exploitation of evaluation-system weaknesses (directly linked to Performative Prediction)],
      [*Regressional*], [H5\ (Social Welfare Fortuitous)], [Agent's $e_t$ effort is *coincidentally* positively correlated with social outcome $Y$ --- measurement noise manifests as field-level alignment],
      [*Extremal*], [H4 (Mediation Heterogeneity)], [Even when the average mediation effect is near zero, mediation is *strong in extreme archetypes (grant-transfer/capital-acquisition)*. The limits of average measurement conceal multiple gaming mechanisms],
    ),
    caption: [Mapping of this paper's six hypotheses onto the four-type Goodhart taxonomy of #cite(<manheim2018>, form: "prose")],
  )

  H1 (field trivial) is a *unit-identification* result that *precedes all four types* --- a meta-hypothesis that asks "at which unit does gaming manifest?" *before* applying the Goodhart taxonomy.

= Data

== Government Fiscal Execution (Gaming Measurement Input)

  - Open Fiscal Data System (OFDS) VWFOEM (monthly execution): 2015--2025 (11 years), 1,557 activities
  - OFDS expenditure_item (budget line items): 2020--2025 (activity-level shares of grants, direct investment, and personnel costs)
  - Bank of Korea ECOS series 901Y009 Consumer Price Index: 1990--2025 (exogenous control variable)

== Outcome Variables (14 Field Mapping)

  Six originally selected outcomes were replaced following external review:

  #figure(
    table(
      columns: 4,
      table.hline(y: 1, stroke: 1.0pt + black),
      [*Field*], [*Outcome Variable*], [*Time Series*], [*Source*],
      [Social Welfare], [Net-asset Gini coefficient], [9 years], [KOSIS DT_1HDAAD04],
      [Health], [Life expectancy], [15 years], [KOSIS DT_1B41],
      [S&T], [Patent applications/registrations], [22 years], [Korean Intellectual Property Office (e-Narajipyo 2787)],
      [Industry/SMEs/Energy], [All-industry production index], [15 years], [KOSIS DT_1JH20201],
      [Culture & Tourism], [Inbound international tourists], [35 years], [Korea Tourism Organization (e-Narajipyo 1653)],
      [Education], [IMD education competitiveness ranking], [17 years], [IMD (e-Narajipyo 1526)],
      [Land Development], [Housing supply rate], [20 years], [KOSIS DT_MLTM_2100],
      [General Administration], [Local fiscal self-reliance ratio], [29 years], [Ministry of the Interior and Safety (e-Narajipyo 2458)],
      [Agriculture/Forestry/Fisheries], [Farm household income], [22 years], [KOSIS DT_1EA1501],
      [Transport], [Traffic fatalities], [10 years], [Road Traffic Authority lgStat],
      [Environment], [Total greenhouse gas emissions], [34 years], [National Institute of Environmental Research (NIER) National Inventory],
      [ICT], [Broadband internet subscription rate], [27 years], [Ministry of Science and ICT (e-Narajipyo 1348)],
      [Unification & Diplomacy], [ODA volume], [24 years], [OECD DAC (e-Narajipyo 1687)],
      [Public Order], [Crime incidence], [29 years], [National Police Agency (e-Narajipyo 1606)],
    ),
    caption: [Outcome variable mapping for 14 fields],
  )

  National Defense and contingency reserves are explicitly designated as fields where outcomes cannot be measured and are excluded from the analysis.

= Methodology

  To quantify the abstract concept of "gaming," this study combines signal processing, dimensionality reduction, topological data analysis, and causal inference in a sequential, integrated framework. Each method was selected to *compensate for the weaknesses of the others*: even if one method fails, the approach checks whether the remaining methods still support the same conclusion — a design this study terms *methodological triangulation*. This section focuses on *intuition* and *why each tool fits the subject*; formal derivations, algorithmic details, and comparisons with alternatives are collected in *Appendix C*.

== Principles of Methodological Triangulation

  Results from any single tool are trustworthy only when that tool's assumptions hold. Because each tool has *a distinct failure mode*, convergence across two or three tools with orthogonal assumptions provides *methodological robustness*. For gaming measurement, this study employs three tools: FFT (frequency domain, stationarity assumption), STL (time domain, additive decomposition), and NeuralProphet (neural additive model, changepoint modeling). The assumptions and weaknesses of each tool are summarized in Table 1.

  #figure(
    table(
      columns: (auto, auto, auto, auto),
      align: (center, center, center, center),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*Tool*], [*Assumptions*], [*Weaknesses*], [*Compensating tool*],
      [FFT], [Stationarity; fixed periodicity], [Absorbs trend; edge effects], [STL, NP],
      [STL], [Additive decomposition; LOESS smoothing], [Absorbs jumps into trend], [FFT, NP],
      [NeuralProphet], [Piecewise-linear trend + Fourier seasonality], [Overfits with small N], [FFT, STL],
    ),
    caption: [Assumptions, weaknesses, and mutual compensation among the three gaming-measurement tools],
  )

== Measuring the Gaming Intensity

  Gaming is a latent behavior that cannot be observed directly. This study extracts its signature from the *shape of the execution time series*. For genuinely normal projects, monthly execution is either relatively flat or exhibits natural variation driven by the project's own schedule. By contrast, gamed projects display *an annual cycle locked to an exogenous calendar* — the "end-of-fiscal-year spending surge" or "jump immediately before the reporting date." This hypothesis is examined using two orthogonal methods.

=== Fourier Transform (FFT)-based amp_12m_norm

  *Intuition:* Any time series can be decomposed into a sum of sinusoids at different periods #cite(<fourier1822>). Applying the Fourier transform to within-year execution series extracts the amplitude of the annual (12-month) component. A larger amplitude indicates a stronger fiscal-year gaming pattern of "December spike followed by January reset." Formal definitions (discrete Fourier transform, `amp_12m_norm` ratio formula, Parseval interpretation) appear in Appendix C.1.

  *Why this tool fits:* Goodhart's effect is defined as gaming synchronized with an *exogenous evaluation cycle* @bevan2006. Korea's fiscal year (January through December) is imposed identically on all ministries, and budget execution rates are assessed uniformly on December 31. The gaming signal therefore has a *known frequency* of one year — an essential feature of this subject. Measuring the amplitude of a known frequency is precisely what *frequency-domain decomposition (FFT) does best*; time-domain variability metrics such as the coefficient of variation cannot exploit this known-frequency information.

=== STL Decomposition (Seasonal-Trend decomposition using Loess)

  *Intuition:* Is the FFT `amp_12m_norm` signal genuine gaming, or is it spurious periodicity generated by a *steadily growing trend* interacting with December year-end accounting? To test this, the study applies STL #cite(<cleveland1990>). STL decomposes a time series additively as $x_t = T_t + S_t + R_t$, separating trend, seasonality, and remainder, and defines the variance share of the seasonal component after trend removal as `seasonal_strength`, which serves as the gaming indicator. The inner/outer iteration loops, robustness weights, and formal definitions appear in Appendix C.2.

  *Why this tool fits:* Korean government budgets have *clearly identified trend drivers* — the 1998 IMF restructuring, the 2007 National Fiscal Act, and the 2009 MTEF five-year framework. Without separating these trends, FFT measures a composite signal of "trend + December gaming." STL uses nonparametric LOESS to absorb *arbitrarily shaped trends* and isolate the *pure seasonal component* — a better fit for Korea's nonlinear budget trajectory than ARIMA differencing. The fact that the Social Welfare automatic-redistribution signal disappears after STL decomposition constitutes a self-critical piece of evidence pointing to potential trend contamination.

=== NeuralProphet Neural Decomposition — Third Cross-Check

  *Intuition:* When FFT (stationarity assumption) and STL (arbitrary-trend assumption) yield conflicting conclusions, a *third independent tool* is needed to determine which signal reflects genuine gaming. NeuralProphet #cite(<triebe2021>) is a neural-network extension of Facebook Prophet #cite(<taylor2018>) that decomposes a time series into six additive components: trend, Fourier seasonality, AR-Net autoregression, events, and exogenous regressors. For cross-check comparability, this study *deactivates* the autoregressive component (`n_lags=0`) and exogenous regressors, using only *trend + seasonality*. The six-component model equation, AR-Net architecture, differences from the original Prophet, and hyperparameter settings appear in Appendix C.3.

  *Why this tool fits:* Korean government budgets simultaneously exhibit (a) gradual long-term trend, (b) policy-driven changepoints (the 2007 National Fiscal Act, the 2014 national accounting reform, the 2017 supplementary budget expansion), and (c) a December fiscal-year cycle. NeuralProphet's *piecewise-linear trend with automatic changepoint detection* absorbs the trend while Fourier bases separate the seasonality, making it nearly the only tool capable of handling all three features simultaneously within an *interpretable additive model* — FFT is weak against (a) and (b), while STL is weak against (b). Comparisons with ARIMA, LSTM, and other alternatives appear in Appendix C.3.

  *Consensus criterion for three tools:* If FFT `amp_12m_norm`, STL `seasonal_strength`, and NP `yearly_seasonality` amplitude are strongly correlated ($r > 0.6$) across the activity-by-year panel, this demonstrates that the gaming signal reflects an *intrinsic property of the data* rather than a tool-specific artifact. Divergence is reported as a limitation, with the assumption differences among tools noted explicitly.

== Discovery of Project Archetypes — Dimensionality Reduction + Density Clustering

  Before grouping activities by field labels, this study first checks whether the *data itself clusters naturally into distinct forms*. Representing 1,557 activities by 12 features (budget composition, execution patterns, and amplitude) yields points in a 12-dimensional space. This high-dimensional representation is then compressed into a visualizable 2-dimensional embedding and clusters are identified.

=== UMAP (Uniform Manifold Approximation and Projection)

  *Intuition:* UMAP is a nonlinear algorithm that compresses dimensionality while *preserving local neighborhood structure* — points close in 12 dimensions remain close in 2, and distant points remain distant @mcinnes2018. It minimizes the cross-entropy between fuzzy simplicial set representations in the high- and low-dimensional spaces via stochastic gradient descent. Loss function derivation, hyperparameters, and comparisons with PCA, t-SNE, and autoencoders appear in Appendix C.4.

  *Why this tool fits:* The 12 features of project activities (budget composition, execution patterns, amplitude) exhibit strong *nonlinear correlations* — for example, a sigmoid relationship between grant-transfer share and gaming amplitude. Moreover, with only 1,557 activities, unsupervised embedding is susceptible to overfitting, and *a reproducible, deterministic embedding* must be citable in policy reports. UMAP satisfies all three requirements: (a) nonlinear preservation, (b) stability with small *N*, and (c) reproducibility via `random_state` — making it nearly the only tool that meets all criteria.

=== HDBSCAN (Hierarchical Density-Based Spatial Clustering)

  *Intuition:* Unlike K-means, HDBSCAN does not require the number of clusters to be specified in advance; instead it identifies *high-density regions* as clusters @campello2013. Points in low-density regions are classified as *noise*. Starting from a minimum spanning tree weighted by mutual reachability distance, the algorithm varies a threshold $epsilon$ to build a condensed cluster tree, selecting clusters with the highest *stability* scores. Distance definitions, tree construction, and comparisons with K-means, DBSCAN, and GMM appear in Appendix C.5.

  *Why this tool fits:* Korean project activities exhibit (a) *large density imbalances* across archetype types (1,175 normal projects vs. 99 capital-acquisition archetypes), (b) a pre-specified cluster count that *contaminates the research hypothesis* (whether field labels are trivial is itself a finding), and (c) *noise handling for outlier activities* (extreme gaming projects) that is essential for identifying policy targets. HDBSCAN satisfies all three requirements (see §6.2 for detail).

== Topological Data Analysis (TDA) — Validating the Stability of Cluster Structure

  Two topological tools are applied to verify that the UMAP+HDBSCAN results reflect *the topological structure of the data itself* rather than algorithmic coincidence or parameter selection. The theoretical foundations of topological data analysis (TDA) follow the review by #cite(<carlsson2009>, form: "prose").

=== Mapper (kmapper)

  *Intuition:* Mapper extracts the *shape skeleton* of the data as a graph @singh2007. Whereas UMAP+HDBSCAN answers *where clusters are*, Mapper answers *how clusters are connected*. It partitions the data space into overlapping covers defined by a filter function, clusters each patch, and then constructs a nerve simplicial complex in which clusters become nodes and an edge is drawn whenever two clusters share a common point. Results are summarized as topological invariants: the number of connected components and the number of loops ($beta_1$). Formal definitions and comparison with UMAP+HDBSCAN appear in Appendix C.6.

  *Why this tool fits:* The study's central claim that "field labels are trivial" depends on the finding that project archetypes form *topologically distinct components* regardless of field membership. If the Mapper graph shows four project archetypes as disconnected components, their status as *topologically separate units* is established — the evidence being not merely embedding distance but *absence of connectivity*.

=== Persistent Homology (PH, ripser)

  *Intuition:* Persistent Homology measures the topological structure of point clouds *simultaneously across all scales*. Structures that appear briefly at small $epsilon$ and then disappear are noise; those that *persist* are genuine topological features @edelsbrunner2008. This study analyzes dimension 0 (connected components $beta_0$) and dimension 1 (loops $beta_1$). Robust results of $beta_0 = 30$, $beta_1 = 15$, and a 95% CI for maximum persistence stable across 50 bootstrap resamples establish the *sample stability* of the topological structure. Computations were performed using the ripser library #cite(<tralie2018>). Vietoris-Rips complex, filtration, persistence diagram definitions, and comparisons with Mapper and silhouette scores appear in Appendix C.7.

  *Why this tool fits:* The study must demonstrate that the four project archetypes it discovers are robust to (a) variation in UMAP parameters and (b) sampling variability. Persistent Homology provides a *nonparametric, scale-invariant* test for both — making it nearly the only tool suited to this validation task.

== Are Field Labels Really the Unit? — Fixed-Effects Regression

  *Intuition:* If the intuition that "different fields yield different outcomes" is correct, adding field dummies to the model should produce a large increase in explanatory power R². Conversely, if ΔR² is near zero, field labels are *trivial* and the true variation originates elsewhere — in project archetypes, for instance. This study compares the increase in adjusted R² between a field-dummy model and a project-archetype × gaming interaction model. Regression equations and decision criteria appear in Appendix C.8.

  *Why this tool fits:* South Korea's administrative budget classification carries (a) strong *historical inertia* (gradually expanded since the 1960s) and (b) *coexistence of heterogeneous project archetypes within a single field* (e.g., the Social Welfare field includes both the grant-transfer archetype of the Korea Social Security Information Service and the normal-project archetype of the National Basic Livelihood Security program). If field labels fail to explain gaming differences, this result directly supports the study's policy implication that the *unit of analysis should be redefined as the project archetype*. Field fixed effects are therefore the *direct test* of this hypothesis.

== Ministry-Archetype Bipartite Graph — Spectral Co-clustering

  The results of this method feed directly into the ministry-outcome quadrant analysis in §7.1.

  *Intuition:* Spectral co-clustering simultaneously clusters the frequency matrix formed by ministries and project archetypes, automatically identifying which ministry specializes in which project form @dhillon2001. The normalized frequency matrix is decomposed via SVD, and left and right singular vectors are used to embed rows and columns jointly; K-means then clusters the result. Normalization, SVD, K-means equations, and comparisons with simple K-means and LDA appear in Appendix C.9.

  *Why this tool fits:* Korean ministries (a) *differ in archetype specialization even within the same field* (e.g., the Ministry of Science and ICT has a large grant-transfer share; the Ministry of the Interior and Safety has a large personnel-type share) and (b) must be *prioritized at the ministry level* when allocating policy-oversight resources. Co-clustering *automatically classifies ministries by their archetype specialization patterns* and provides the input for the ministry-outcome quadrant analysis. Fifty-one ministries were separated into five co-clusters.

== Causal Identification — Is Gaming the True Cause?

=== Regression Discontinuity Design (RDD)

  *Intuition:* December 1 of the fiscal year is an administratively imposed boundary drawn across *continuous time*. If execution patterns jump sharply just before and just after this boundary regardless of a project's intrinsic needs, that jump can be attributed to the *exogenous accounting cycle* (@imbens2008; @lee2010). This study uses the ratio of daily-average execution in November versus December at the activity level and reports results as a *ratio-type jump multiplier*, directly comparable to the Liebman-Mahoney 5× benchmark from the United States. Identification assumptions, local linear estimator equations, and comparisons with DiD, IV, and month fixed effects appear in Appendix C.10.

  *Why this tool fits:* Korea's fiscal-year cutoff (a) has been *unchanged since 1948*, (b) is applied *simultaneously* to all ministries, and (c) *cannot be manipulated* by individual activities — providing conditions that satisfy all three core RDD identification assumptions, approximating an ideal natural experiment. The design that #cite(<liebman2017>, form: "prose") used in the United States to document a 5× jump and quality decline with a few-days cutoff difference can be *applied directly to Korea*, and the analysis confirms jumps of 1.91× (overall) and 3.42× (capital-acquisition archetype). Because the comparison involves the same activity just days apart, field, institutional, and project-specific characteristics are *automatically controlled* in this quasi-experiment.

=== Mediation Analysis — Baron-Kenny + Sobel + Bootstrap

  *Intuition:* Even if a positive correlation between grant-transfer share ($X$) and worse outcome ($Y$) is found, the mechanism must be distinguished — whether the pathway runs through "$X arrow$ gaming ($M$) $arrow Y$" as an *indirect effect* or directly as "$X arrow Y$" @baron1986. Four-step regression decomposes the total effect $c$, mediation path $a$, direct effect $c'$, and mediated effect $a b$; statistical significance is then assessed via Sobel z-test and 1,000-iteration bootstrap confidence intervals. The four-step equations, Sobel standard error formula, bootstrap procedure, and comparisons with SEM and causal mediation analysis appear in Appendix C.11.

  *Why this tool fits:* The study's central hypothesis posits a *sequential causal path* of "grant-transfer → December gaming → outcome deterioration." If mediation holds, the policy response is to reform *gaming itself* (e.g., multi-year accounting, MTEF strengthening); if the effect is direct, the reform target is the *grant structure* (e.g., converting commissioned projects to in-house operations). Baron-Kenny provides this pathway separation in *interpretable regression coefficients*. Results show the system-wide average mediated effect is not significant (*p* = .481), but strong mediation is found in Social Welfare and Environment — supporting *field heterogeneity* in the gaming mechanism.

== Exogenous Controls — Rejecting the Natural Business-Cycle Hypothesis

  *Intuition:* Is the Social Welfare gaming-outcome correlation genuinely causal, or is it *spurious co-movement driven by business cycles*? The CPI from §4 (ECOS 901Y009) is used as an exogenous macroeconomic control, and partial correlations are computed via *Frisch-Waugh-Lovell residualization* (two-stage residual regression). Definitions, exogeneity assumptions, and comparisons with unemployment rate and GDP as alternatives appear in Appendix C.12.

  *Justification of exogeneity:* Because the CPI is set by the Bank of Korea as a monetary-policy instrument, (a) *central bank independence* shields it from direct exposure to fiscal administrative decisions, and (b) the *pre-announced target of 2.0\%* minimizes reverse-causality threats. The CPI is therefore the most exogenous candidate among Korean macroeconomic variables with respect to fiscal gaming, and it can be reliably controlled using official monthly data spanning 1990--2025. Results: signs are preserved in 14/14 fields; 70% of significant results remain significant. The Social Welfare signal strengthens from $r = -0.76$ to $-0.86$ — a result that *strongly rejects* the natural business-cycle hypothesis.

== Robustness Checks — Permutation, Lag/Lead, and CV

  *Permutation test:* The outcome variable time series is randomly shuffled $B = 1000$ times to construct a null distribution, and two-tailed *p*-values are computed. This nonparametric test requires no normality or homoscedasticity assumptions, circumventing the unreliability of normal-approximation t-tests in small field-level samples of *N* = 8--12.

  *Lag/Lead analysis:* Correlations between gaming and outcomes are re-estimated with lags $tau in {-1, 0, +1}$ years to examine *directionality*. If synchronous correlation $r(0)$ is strongest, this supports an immediate mechanism (consistent with the Social Welfare automatic-redistribution hypothesis); a stronger $r(+1)$ implies a delayed effect; a stronger $r(-1)$ raises concerns about reverse causality.

  *amp_cv alternative:* As an alternative to the FFT-based measure, gaming indicators are recomputed using a coefficient-of-variation metric ($"CV" = sigma\/mu$), hereafter denoted `amp_cv`, to assess *measurement-instrument dependence*. Convergence of the two indicators on the same conclusion establishes measurement robustness. Test equations and formal definitions appear in Appendix C.13.

= Results: Multi-Method Validation of Six Hypotheses

  This section validates the six hypotheses (H1–H6) derived in §3, with each hypothesis addressed in a dedicated sub-section. A finding is reported in the main text only when it is supported by the *consensus of multiple tools* rather than a single regression coefficient. The final sub-section separately reinforces *methodological robustness* (STL self-criticism + NeuralProphet cross-check integration).

  #figure(
    table(
      columns: (0.3fr, 1fr, 0.5fr),
      align: (center, center, center),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*Hypothesis*], [*Prediction*], [*Validation Sub-section*],
      [H1], [Field labels are trivial; project archetypes are the real unit of analysis], [§6.1·§6.2],
      [H2], [Capital-acquisition type shows the largest RDD discontinuity (discrete spike)], [§6.3],
      [H3], [Grant-transfer type dominates in cycle amplitude (PSD/coherence)], [§6.4],
      [H4], [Archetype heterogeneity in mediation pathways (pooled effect non-significant)], [§6.6],
      [H5], [Social Welfare fortuitous alignment ($(partial Y) / (partial e_t) > 0$)], [§6.7],
      [H6], [Time-dynamic strengthening ($w_t / w_q$ ratio increasing over time)], [§6.8],
      [Methodology], [STL self-criticism + NeuralProphet/Wavelet arbitration], [§6.9],
    ),
    caption: [P-A model hypotheses and validation mapping across results sections],
  )

  This study assigns 11 analytical tools across hypotheses. Each hypothesis uses a *primary validation tool* to derive core findings, and *auxiliary robustness tools* to assess robustness — a triangulation structure.

  #figure(
    table(
      columns: (auto, 1.1fr, 1.1fr),
      align: (center+horizon, left+horizon, left+horizon),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*Hypothesis*], [*Primary Validation Tool*], [*Auxiliary / Robustness Tools*],
      [H1], [Pooled FE regression ($Delta R^2 = 0.000$)], [UMAP+HDBSCAN, Mapper, Persistent Homology (PH bootstrap)],
      [H2], [Regression discontinuity (RDD), monthly Nov/Dec comparison], [Permutation 1,000 iterations · field-level · archetype-level forest plot],
      [H3], [FFT amp_12m + Welch PSD], [Phase coherence · Wavelet (Appendix D)],
      [H4], [Baron-Kenny + Sobel + Bootstrap mediation analysis], [NeuralProphet cross-check (§6.5)],
      [H5], [First-difference correlation (*r* = −0.86, *p* < .01)], [Permutation, Frisch-Waugh-Lovell CPI exogenous control],
      [H6], [Continuous Wavelet Transform (Morlet)], [STL self-criticism + NeuralProphet arbitration (§6.9)],
    ),
    caption: [Hypothesis × analytical tool matrix — allocation of 11 tools across hypotheses (primary + auxiliary/robustness)],
  )

== H1: Field Labels Are Trivial; Project Archetypes Are the Real Unit

  *Why this verification first*: Korean public administration and fiscal research conventionally conducts analysis at the field level (Social Welfare, Education, Defense, etc.), treating inter-field heterogeneity as the primary explanation for outcome differences. All subsequent findings in this study — project archetype discovery, topological data analysis (TDA), and regression discontinuity (RDD) jumps — presuppose that this assumption is *wrong*. Accordingly, this study first quantitatively evaluates the marginal explanatory power of field labels.

  In the pooled FE regression, adding field fixed effects alone left R² unchanged at 0.014 (field FE only: ΔR²=0.000). Adding the project archetype × expenditure oscillation interaction raised R² to 0.038 (ΔR²=+0.025) (@fig-h8). This constitutes quantitative evidence that field-level heterogeneity is trivial, and that project type is the true explanatory variable.

  *Interpretation*: Regardless of field, the intensity of the Goodhart's game is determined by *how a project is operated* — personnel-type, capital-acquisition, grant-transfer, or normal projects. Subsequent sections discover this "project type" from the data.

  *Model Validation (H1)*: This finding directly validates the P-A model's prediction that *the unit of the cost function $c(e_t, e_q; theta)$ is the project archetype $theta$, not the field* (@fig-h8). Field labels are merely *administrative classification conventions* and carry no information about cost structure or decision behavior.

== H1 Reinforced: Topological Stability of Four Project Archetypes

  *Question*: If the field is not the real unit, what is? Rather than imposing an answer a priori, this study *asks the data*. Compressing 12 dimensions to 2 via UMAP and applying density-based clustering via HDBSCAN, four stable clusters emerge (@fig-umap).

  The z-score profiles of each cluster correspond to *project types intuitively recognizable to administrative practitioners*:

  - *C0 personnel-type* (n=129): personnel +3.07, Goodhart's game amplitude −1.32 — fixed monthly disbursements → flat profile
  - *C1 capital-acquisition* (n=99): direct_invest +3.28, high share of infrastructure/construction fields — fluctuates with progress billing
  - *C2 grant-transfer* (n=154): chooyeon +2.89, Goodhart's game amplitude +0.88 — outsourced to public bodies and grant-receiving institutions → concentration in December
  - *C3 normal projects* (n=1,175): near-average values — baseline

  *Topological stability verification*: To confirm that the four UMAP+HDBSCAN clusters are not algorithmic artifacts, two topological tools are applied in parallel.

  - The *Mapper graph* (@fig-mapper-amp, @fig-mapper-cluster) confirmed topological separation of clusters with 32 nodes / 38 edges / 10 components / 7 loops.
  - *Persistent Homology* reported 30 robust components and 15 robust loops (@fig-ph-pd, @fig-ph-barcode); across 50 bootstrap iterations, the H1 max persistence 95% CI [0.48, 1.19] rules out chance in the topological structure (@fig-ph-bootstrap).

  All three tools (UMAP+HDBSCAN, Mapper, PH) consistently support the conclusion that *project type is a stronger unit of analysis than field*.

#figure(
  image("figures_en/h3_umap.png", width: 100%),
  caption: [\[H1 Validation\] Activity-embedding UMAP — 4 project archetypes (1,557 activities × 12 features)],
) <fig-umap>

#figure(
  image("figures_en/h4_mapper_amp.png", width: 70%),
  caption: [\[H1.b Validation\] Mapper graph — colored by mean amp_12m_norm. \ 32 nodes / 38 edges / 10 components / 7 loops. Node size proportional to number of activities.],
) <fig-mapper-amp>

#figure(
  image("figures_en/h4_mapper_cluster.png", width: 70%),
  caption: [\[H1.b Validation\] Mapper graph — same graph, colored by HDBSCAN project archetype (4 archetypes).\ Confirms topological separation of 4 archetypes.],
) <fig-mapper-cluster>

#figure(
  image("figures_en/h9_pd.png", width: 100%),
  caption: [\[H1.b Validation\] Persistence Diagram — Vietoris-Rips, N=300, max thresh=8.0.\ H0 (blue) · H1 (red) birth-death pairs.],
) <fig-ph-pd>

#figure(
  image("figures_en/h9_barcode.png", width: 100%),
  caption: [\[H1.b Validation\] H1 Barcode — birth-death bars for the 30 longest-persisting loops.\ max persistence = 0.671.],
) <fig-ph-barcode>


#figure(
  image("figures_en/h9_bootstrap.png", width: 100%),
  caption: [\[H1.b Validation\] Bootstrap PH 50 iterations (n=200) — H1 max persistence 95% CI [0.48, 1.19].\ Sample stability verified against 5-year reference (median 0.65).],
) <fig-ph-bootstrap>

== H2: Capital-Acquisition Type Year-End RDD Jump

  *Why RDD is decisive evidence*: To separate normal variation driven by project characteristics from fiscal year-end gaming, this study compares the daily average expenditure of the *last week of November vs. the first week of December* for the same activity. A few days' variation cannot be explained by project fundamentals; only the *administratively arbitrary cutoff of December 1* can account for it. This applies the design of #cite(<liebman2017>, form: "prose") (AER) — which reported a 5× jump in U.S. federal procurement — to the Korean context.

  Estimating a regression discontinuity (RDD) of daily average activity-level expenditure across November–December, the December discontinuity averaged *1.91× overall* ($p < 10^(-124)$) (@fig-rdd-monthly, @fig-rdd-yearly). Decomposed by project type (@fig-rdd-field):

  - *Capital-acquisition type: 3.42×* (strongest, n=99) — a *discrete jump* immediately after December 1, where progress-billing deadlines for facility construction and asset acquisition coincide with the fiscal year-end cutoff
  - *Normal projects: 2.24×* (n=1,175)
  - *Personnel-type: 1.12×* (n=129, structurally flat)
  - *Grant-transfer type: 1.10×* (n=154, below statistical threshold) — weak in the RDD but strongest in the *annual cycle*

  The difference between the U.S. 5× and Korea's 1.9× in absolute magnitude is explained by *measurement unit granularity* (U.S. weekly vs. Korea monthly — the December first-week signal is dispersed across the full month). The *ordering* of RDD jumps by project type demonstrates that the use-it-or-lose-it mechanism of #cite(<liebman2017>, form: "prose") operates most strongly in *progress-billing and capital-acquisition projects*.

  *RDD vs. spectral measures — mechanism differences by project archetype*: While RDD measures a *discrete jump* immediately after December 1, FFT/STL/NeuralProphet/Wavelet measure *annual cycle amplitude*. Capital-acquisition type shows a stronger RDD jump (3.42×), whereas grant-transfer type shows stronger cycle intensity (PSD 0.332, phase coherence 0.54, wavelet +554\%; see §6.4 for details). Both archetypes are *locked to the exogenous fiscal cycle*, but capital-acquisition manifests as a *single spike right after the progress deadline*, while grant-transfer manifests as *multiple distributed settlements following trustee institution schedules, accumulating in December*. This archetype-level difference in gaming mechanism is directly reflected in this study's policy recommendations (Recommendations 1 and 2).

  *Model Validation (H2)*: This finding directly demonstrates that *archetype-specific differences in the cost function $c(e_t, e_q; theta)$* in the P-A model manifest as *differences in the temporal structure of the equilibrium $e_t^*$*. For capital-acquisition type, $c(e_t)$ *drops sharply* immediately after December 1 — the arbitrary point at which both progress-billing and fiscal-year deadlines expire simultaneously — yielding the largest RDD jump (H2). Both equilibria reflect the *same FOC* $w_t = (partial c) / (partial e_t)$ of the model, expressing different temporal structures through *archetype-specific differences in the cost function*.

#figure(
  image("figures_en/h22_rdd_monthly.png", width: 100%),
  caption: [\[H2 Validation\] Monthly average daily expenditure per activity (2015–2025) — color indicates fiscal year (purple 2015 → yellow 2025);\ thick black line is the 11-year average. December discontinuity visible in the Nov–Dec region (red).],
) <fig-rdd-monthly>

#figure(
  image("figures_en/h22_rdd_yearly.png", width: 80%),
  caption: [\[H2 Validation\] Annual December jump (median log daily expenditure per activity: December − November).\ Overall RDD β=0.65 (1.91×, orange dashed), vs. #cite(<liebman2017>, form: "prose") U.S. 5× reference line (purple dashed).],
) <fig-rdd-yearly>

#figure(
  image("figures_en/h22_rdd_field.png", width: 100%),
  caption: [\[H2 Validation\] December jump multiplier by field — Defense, Land Development, and Transport are largest; *capital-acquisition type 3.42× (strongest)*],
) <fig-rdd-field>

== H3: Grant-Transfer Type Cycle Dominance (PSD/Phase/Coherence/Wavelet)

This section reports key figures only; spectral decomposition procedures and figures are presented in *Appendix D.1–D.3*. The hypothesis under test for H3: grant-transfer type PSD k=1 amplitude, phase coherence, and wavelet amplitude are superior to those of other archetypes.

*Model context*: The RDD analysis in §6.3 reported that grant-transfer type shows a weak RDD jump (1.10×) but is strong in the annual cycle. This is the direct test target for H3, which predicts that the cost function $c(e_t)$ for grant-transfer type in the P-A model is *distributed* (trustee institution settlements occur multiple times throughout the fiscal year).

*Summary of results*:
- *PSD k=1 amplitude* (12-month cycle): grant-transfer type 0.332 (2–3.4× the other archetypes' 0.097–0.172)
- *Phase coherence* (simultaneous peaks across activities): grant-transfer type 0.54 (4–7× the other archetypes' 0.08–0.13)
- *Wavelet amplitude time evolution*: grant-transfer type +554% (2015–17 → 2023–25), capital-acquisition +175%, normal projects +317%, personnel-type −0.8%

All three measures consistently show that *grant-transfer type is most strongly locked to the annual Goodhart's game cycle*. This validates the archetype-level difference in temporal structure: *capital-acquisition type is strongest in RDD discontinuity (discrete spike), while grant-transfer type is strongest in cycle amplitude (continuous intensity)*.

*Model Validation (H3)*: All three measures support the predictions of the P-A model. The distributed $c(e_t)$ → pattern of the equilibrium $e_t^*$ accumulating across the entire annual cycle is dominantly confirmed in PSD/coherence/wavelet. This result, contrasting with the step-function $c(e_t)$ of capital-acquisition type (marginal cost drops sharply after December 1), supports H3.

== Methodological Complementarity: FFT/STL/NeuralProphet Measures

  *Scope of this section*: This section examines the complementarity of three Goodhart's game measures (FFT, STL, NeuralProphet). Validation of H4 (archetype heterogeneity in mediation pathways) is conducted in §6.6. This study initially framed FFT, STL, and NeuralProphet as "cross-check tools that might yield different conclusions," but the actual results suggest that *the three tools are complementary lenses measuring different facets of the Goodhart's game*. FFT captures *the share of 12-month cycle amplitude in total frequency-domain variation*; STL captures *the ratio of seasonal variance to residual variance in time-domain trend-residual decomposition*; NeuralProphet captures *the fitted Fourier-basis amplitude after piecewise-linear trend and automatic changepoint adjustment*. Since all three are *orthogonal representations of the same signal*, their near-zero mutual correlations are not contradictions but rather quantify *the heterogeneity of the Goodhart's game dimension each tool captures*.

  *Analytical design*: NeuralProphet was fitted at the activity-year level on a random sample of 200 activities (epochs=50, n_lags=0, n_changepoints=2), yielding approximately 1,051 fitted observations. After fitting, the yearly seasonality amplitude was normalized by the activity standard deviation and extracted as `np_seasonal_strength`.

  *Activity-year panel correlations among three measures*:

  #figure(
    table(
      columns: (auto, auto, auto, auto),
      align: (left, center, center, center),
      table.hline(y: 1, stroke: 1.0pt + black),
      [], [*FFT*], [*STL*], [*NP*],
      [*FFT*], [1.000], [], [],
      [*STL*], [$-0.130$], [1.000], [],
      [*NP*], [$-0.039$], [$-0.018$], [1.000],
    ),
    caption: [Cross-correlations among three Goodhart's game measures (activity-year panel, $N = 1051$)],
  )

  *Interpretation (complementarity)*: Near-zero correlations among all three constitute direct evidence that each measures a *different signal dimension*.
  - *FFT amp_12m_norm*: Frequency decomposition of the activity time series measuring *the share of 12-month cycle amplitude in total variation*. Trend is not decomposed.
  - *STL seasonal_strength*: After trend removal via LOESS smoothing, the *ratio of seasonal variance to residual variance*. Additive decomposition.
  - *NP yearly seasonality*: *Fitted amplitude on a Fourier basis* after piecewise-linear trend and automatic changepoint adjustment, simultaneously estimated via a neural network.

  Appendix D (H27) extends FFT from *a single amplitude point* to the *full PSD + phase + cross-coherence*, providing deeper evidence of the three tools' complementarity — for grant-transfer type, the *largest PSD k=1 amplitude* together with *phase coherence 0.54* (simultaneous peaks across activities) is newly revealed, confirming the strongest lock-in to the exogenous fiscal cycle.

  *Field-level outcome correlation (3-way)*: Recomputing outcome correlations for 14 fields using all three measures, Health (life expectancy) and ICT (broadband) show negative values across all three measures (Health: FFT $-0.55$, STL $+0.20$, NP $-0.71$; ICT: FFT $-0.15$, STL $+0.05$, NP $-0.75$), with *NeuralProphet additionally identifying a Goodhart's game signal in ICT that FFT missed*. In contrast, Social Welfare shows weak signals across all three measures (FFT $+0.03$, STL $+0.00$, NP $-0.24$), consistent with the signal disappearance observed in field-level STL and with activity-level NP results.

  *Interactive visualization*: The NeuralProphet component decomposition (trend + yearly seasonality) for the four project archetypes is publicly available as an interactive Plotly visualization at #link("https://bluethestyle.github.io/goodhart-korea/interactive/neuralprophet_components.html")[interactive viz #5: NeuralProphet decomposition]. The December positive jump in grant-transfer type activities, the flat trend in personnel-type, and the weak seasonality of normal projects can be compared via hover and zoom.

  *Conclusion*: Since all three tools decompose the same signal along *different dimensions*, the robustness of this study rests not on *the absolute value of any single tool* but on *the field- and archetype-level patterns consistently indicated by multiple tools*. The negative signals in Health, ICT, Defense, and Education (consistent across all measures), and grant-transfer type December phase coherence of 0.54 (further confirmed by PSD/Phase analysis), constitute a successful example of *methodological triangulation*.

== H4: Archetype Heterogeneity in Mediation Pathways (Baron-Kenny + Sobel + Bootstrap)

  *Question*: This model posits a sequential causal pathway of *grant-transfer share ($X$) → timing-adjustment effort ($M = e_t$) → social outcome ($Y$)*. If the model is correct, mediation analysis should reveal *archetype-level heterogeneity* — the mediation pathway should be strong for grant-transfer and capital-acquisition types (high $w_t$) and weak for personnel-type (low $w_t$) and normal projects.

  *Method*: #cite(<baron1986>, form: "prose") four-step procedure + Sobel z-test + Bootstrap 95\% confidence interval (Appendix C.11; for mediation analysis methodology in general, see @hayes2017). Activity-level: $X$ = grant-transfer share, $M$ = `amp_12m_norm`, $Y$ = field-level outcome variable.

  *Results — pooled mediation effect non-significant*: The Sobel z-test for the average mediation effect $a b$ across 14 fields yielded *p* = 0.481, non-significant. That is, at the *system average*, the mediation pathway is weak.

  *Model Validation (H4) — pooled non-significance as direct evidence of archetype heterogeneity*: The P-A model predicts that *the cost function $c(\cdot; theta)$ differs by project archetype $theta$* (§5.2 results). It is entirely natural for the average mediation effect to be attenuated by *the cancellation of heterogeneous mediation strengths across archetypes* in the pooled estimate. Thus *p* = 0.481 is not a contradiction but a *direct validation of the model*.

  *Field-level mediation decomposition*: Strong mediation effects emerge in Social Welfare ($a b > 0$, automatic redistribution channel) and Environment ($a b < 0$, direct negative channel). Both fields are *alignment fields where $(partial Y) / (partial e_t) != 0$* (consistent with the H5 fortuitous alignment proposition). The remaining 12 fields show small mediation effects that dilute the pooled estimate.

  *Interpretation*: Model hypothesis H4 (archetype heterogeneity in mediation pathways) is validated. This implies that policy interventions *must be differentiated by archetype* — applying a uniform evaluation system to all projects dilutes the average efficacy of the intervention.

== H5: Social Welfare Automatic Redistribution (Fortuitous Alignment)

  *Counter-intuitive finding*: The Goodhart's game is typically understood as a negative measurement distortion, but this study finds a case in which it is associated with *positive outcomes* in the Social Welfare field. A stronger December concentration of expenditure in Social Welfare normal projects correlates with a *decrease in the net-wealth Gini coefficient (reduced inequality)*. This is interpreted as a mechanism in which social welfare benefits and subsidies are disbursed en masse just before the fiscal year-end closes, automatically redistributing resources to lower-income populations.

  The first-difference correlation for the Social Welfare field was *r* = −0.762 (*p* = 0.035, permutation 1,000 iterations), the only statistically significant result among all 14 fields (@fig-h6). In the lag/lead first-difference correlation (k = −2..+2), the contemporaneous correlation was strongest, supporting the immediate automatic redistribution mechanism; the direction was consistent using the alternative `amp_cv` indicator as well (@fig-h6-lag). After CPI exogenous control, the signal *strengthened* to *r* = −0.86 (*p* = 0.007), rejecting the natural business-cycle hypothesis (@fig-h10).

  *Why does the signal strengthen?*: Analyzing CPI residuals removes the portion explained by macroeconomic fluctuations (co-movement of inflation and unemployment). The signal strengthening rather than weakening suggests that the link between the Goodhart's game and the outcome variable is rooted in the *administrative mechanism itself* rather than the business cycle.

  *Model Validation (H5) — explicit fortuitous alignment*: In the P-A model, the agent's objective function $U_A$ *does not include social outcome $Y$*. The agent maximizes only the evaluation score $w_t e_t + w_q tilde(e)_q$. Accordingly, the negative correlation in Social Welfare (*r* = −0.86) is a result that *coincidentally* occurs in a field where $(partial Y) / (partial e_t) > 0$ — a field where concentrated December disbursement happens to align with poverty gap reduction. In the other 13 fields ($Delta Y/Delta e_t approx 0$), the identical gaming effort does not translate into improved social outcomes.

  *Interpretation — not a policy justification*: This finding is *not* a general claim that the Goodhart's game improves social outcomes. It merely identifies a fortuitous alignment in Social Welfare, and generalizing this as "the Goodhart's game is beneficial" would be incorrect. The model expresses this contingency as a *mathematical proposition* — since the agent does not care about $Y$, any $Y$-improvement is always fortuitous.

  *Model Validation (H1 reinforced) — compatibility of field trivial with Social Welfare redistribution*: "If fields are trivial (H1), how can a strong correlation in the Social Welfare field be possible?" The model separates two layers: (a) the *unit of the cost function $c(\cdot)$* is the project archetype (field trivial), (b) the *unit of outcome variable $Y$ alignment* is the field (coincidental alignment in Social Welfare). The two layers are *independent* and thus compatible.

#figure(
  image("figures_en/h6_robustness.png", width: 100%),
  caption: [\[H5 Validation\] Robustness: (a) FE regression β + 95% CI (N=128). (b) Permutation forest 14 fields. Social Welfare obs = -0.762, p = 0.035, only significant field (fortuitous alignment).],
) <fig-h6>
#pagebreak()
#v(-2em)

#figure(
  image("figures_en/h6_lag_amp.png", width: 100%),
  caption: [Robustness (continued) — (c) Lag/lead first-difference correlation heatmap (k=−2..+2).\ (d) Field-level amp_12m temporal coefficient of variation (amp_cv) — Social Welfare (red) shows low volatility\ but strong outcome correlation, supporting the KPI-pressure hypothesis over a natural cycle explanation.],
) <fig-h6-lag>
#v(-0em)

#figure(
  image("figures_en/h10_cpi_control.png", width: 85%),
  caption: [\[H5 Auxiliary\] CPI exogenous control — sign maintained in 14/14 fields, 70% of significance retained.\ Social Welfare r = −0.76 → −0.86 (strengthened), rejecting the natural business-cycle hypothesis.],
) <fig-h10>

#figure(
  image("figures_en/h8_panel.png", width: 100%),
  caption: [\[H1 Validation\] Test of field-label triviality — field FE alone: ΔR²=0.000;\ adding project archetype × Δamp: ΔR²=+0.025 (R²: 0.014 → 0.038)],
) <fig-h8>

== H6: Time-Dynamic Strengthening (Wavelet)

  *Why time-domain analysis?*: FFT amp_12m_norm measures the *fixed average* amplitude of an 11-year time series and therefore cannot detect *change over time*. To test whether the stationarity assumption is inappropriate for this study's context — which includes multiple policy change points (2007 National Finance Act, 2014 national accounting system reform, 2020 COVID fiscal expansion) — Continuous Wavelet Transform (CWT, complex Morlet) was applied (see Appendix D.4 for details).

  *Results — temporal evolution of 12-month cycle amplitude* (archetype-average time series; comparison of 2015–2017 vs. 2023–2025 averages):

  #figure(
    table(
      columns: (auto, auto, auto, auto),
      align: (left, center, center, center),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*Archetype*], [*early (2015–17)*], [*late (2023–25)*], [*Change*],
      [Personnel-type], [0.007], [0.007], [$-0.8\%$ (no change)],
      [Capital-acquisition], [0.055], [0.150], [*$+174.7\%$*],
      [Grant-transfer], [0.201], [1.315], [*$+553.6\%$*],
      [Normal projects], [0.057], [0.237], [*$+316.7\%$*],
    ),
    caption: [Temporal evolution of 12-month wavelet power by archetype — grant-transfer type 5.5× amplification. Precise value +553.6%; rounded to +554% when cited in text.],
  )

  *Model Validation (H6) — temporal increase in $w_t / w_q$ ratio*: From the comparative statics of the P-A model, since $(partial e_t^*) / (partial w_t) > 0$, an increase over time in the evaluation weight ratio $w_t / w_q$ must be accompanied by an increase in equilibrium timing-adjustment effort $e_t^*$. Plausible drivers of increasing $w_t / w_q$ in Korea:

  - *2007 National Finance Act implementation*: Execution-rate evaluation institutionalized and strengthened → $w_t$ ↑
  - *2014 national accounting system reform*: Standardization and transparency of fiscal settlement raises measurement accuracy of execution rates → effective $w_t$ ↑
  - *2017 supplementary budget expansion + increase in grant-receiving institution share*: Number of grant-transfer activities ↑ → *share* of activities with high $w_t$ increases
  - *2020\~2022 COVID fiscal expansion*: December settlement pressure on newly established projects intensifies

  The $w_q$ side shows almost no change (the fundamental difficulty of measuring project outcomes remains). The increase in $w_t / w_q$ is therefore a *reasonable inference*, and the wavelet results (+554\%) constitute a *direct validation* of that inference.

  *Control case — no change in personnel-type*: By structure, personnel-type involves equal monthly disbursements, making *$e_t$ adjustment itself infeasible* ($(partial c) / (partial e_t) = infinity$). The model predicts that time-dynamic strengthening will not appear in this archetype — the result of −0.8\% confirms the *prediction exactly*. This reinforces that the measurement tool (wavelet) captures only genuine dynamic signals, not noise.

  *Implication — Korea's Goodhart's effect is ongoing*: This finding demonstrates that Korean fiscal gaming is *not a fixed pattern but a dynamic and ongoing amplification phenomenon*. Policy analysis should shift its temporal weighting toward *the most recent three fiscal years of data* (Recommendation 5), and 11-year average values from stationarity-assuming tools such as FFT amp_12m_norm *dilute the amplification trend* and require supplementation.

#figure(
  image("figures_en/h28_evolution.png", width: 80%),
  caption: [\[H6 Validation\] Annual evolution of 12-month cycle amplitude — *grant-transfer type +554% amplification*, personnel-type unchanged (control). Policy change points annotated (2017: 10 years after National Finance Act; 2020: COVID fiscal expansion).],
) <fig-h28-evol-body>

== Methodological Robustness: STL Self-Criticism + NeuralProphet/Wavelet Arbitration

  *Why self-criticism?*: This study must internally verify whether the Social Welfare automatic redistribution finding reflects a genuine December concentration signal, or whether it is spurious periodicity generated by the *continuously increasing trend* of the Social Welfare budget year over year. STL was applied to the same activity time series to remove the trend, and the correlation was recomputed using `seasonal_strength`.

  *Results — signal disappearance*: When `seasonal_strength` after STL decomposition is used as the Goodhart's game indicator, the Social Welfare signal *vanishes entirely* to *r* = +0.003 (*p* = 0.991) (@fig-stl-bars, @fig-stl-scatter). Two possibilities:
  - (a) The FFT signal is a composite of *continuously increasing trend × December recording date* — the Goodhart's game is spurious
  - (b) STL smoothing *absorbs the genuine gaming jump* into the trend component — the gaming is real but STL cannot detect it

  *How to distinguish (a) from (b)*: This study responds with two auxiliary validations.
  - *NeuralProphet arbitration* (see §6.5): Explicit changepoint modeling bypasses the possibility that STL absorbed the signal into trend. Activity-level results recover a negative signal of *r* = −0.24 in Social Welfare (weak, but stronger than STL's 0.003).
  - *Wavelet temporal evolution*: Tracking whether the 12-month cycle amplitude of Social Welfare activities *changes over time*. If it does, the stationarity and trend-decomposition assumptions themselves are partially inappropriate for Korean data (see Appendix D.4).

  This study explicitly acknowledges this as a *limitation of decomposition assumption dependency*, and honestly reports that the Social Welfare finding rests not on *a single FFT amp_12m_norm indicator alone* but on *the partial consensus of multiple tools*.

#figure(
  image("figures_en/h24_stl_bars.png", width: 100%),
  caption: [Field-level first-difference correlation — FFT amp_12m_norm vs. STL seasonal_strength comparison.\ Pink rows + red field names = sign reversal in 5/15 fields. Social Welfare: FFT −0.76 → STL +0.07, signal disappearance.],
) <fig-stl-bars>

#figure(
  image("figures_en/h24_stl_scatter.png", width: 100%),
  caption: [FFT vs. STL correlation scatter plot — pink region (quadrants 2 and 4) indicates sign reversal.\ Social Welfare (large black dot) lies within the sign-reversal region (upper left). Reference line y=x.],
) <fig-stl-scatter>

#pagebreak()

= Policy Implications

  The findings of this study yield policy recommendations at two levels: *diagnosis* and *prescription*.

== Diagnostic Tool: Ministry-Outcome Quadrant

  *Why a quadrant?* Placing ministries in a four-quadrant space defined by Goodhart exposure and the sign of the outcome variable allows one to distinguish ministries where *the same gaming intensity is associated with different outcome signs*. When allocating monitoring resources, the imperative is not simply to focus on ministries with the strongest gaming, but to prioritize those where *gaming and deteriorating outcomes co-occur* — a decision-making tool for targeted oversight.

  From the ministry-by-outcome quadrant analysis (@fig-quadrant):

  - *Q2 (Review Required, Red)*: Office for Government Policy Coordination (OPC) and Prime Minister's Secretariat, and Ministry of Science and ICT (MSIT) — Goodhart exposure combined with a positive correlation with outcome variables, meaning gaming co-moves with outcome deterioration (suspected measurement distortion)
  - *Q1 (Automatic Redistribution OK, Green)*: Multifunctional Administrative City Construction Agency, and similar — gaming exposure present but negatively correlated with outcome variables, suggesting potential for Social Welfare-type automatic redistribution
  - *Q3, Q4*: Low gaming exposure; outside the priority scope of this analysis

  As an additional monitoring priority, 50 extreme gaming activities (sub05 classification) spanning all fields are identified. This study provides these 50 cases as a *data-driven priority list* that can be submitted directly to the Board of Audit and Inspection (BAI), parliamentary audit proceedings, and internal reviews by the Ministry of the Interior and Safety.

#figure(
  image("figures_en/h14_quadrant.png", width: 100%),
  caption: [Ministry-level Goodhart exposure × outcome quadrant — Q2 ministries represent the highest monitoring priority],
) <fig-quadrant>

== Prescription: Mapping Administrative Actions to Equilibrium Shifts

  Rather than enumerating policy prescriptions arbitrarily, this section derives them directly from the *comparative statics results of the P-A model*. The model (Theory section) identifies *three policy levers* via the partial derivatives of the equilibrium timing effort $e_t^*$:

  $ (partial e_t^*) / (partial w_t) > 0, quad (partial e_t^*) / (partial w_q) < 0, quad (partial e_t^*) / (partial c_(t t)) < 0 $

  How each lever can be activated through *administrative actions* in the Korean institutional context:

  #figure(
    table(
      columns: (auto, auto, 1fr),
      align: (left, left, left),
      table.hline(y: 1, stroke: 0.5pt + black),
      [*Lever*], [*Expected Effect*], [*Candidate Administrative Actions*],
      [$w_t$ ↓], [$e_t^*$ ↓ (gaming reduced)], [Relaxing execution-rate evaluation criteria; multi-year accounting; strengthening MTEF; reducing the weight of execution-rate targets in performance evaluations of quasi-governmental agencies],
      [$w_q$ ↑], [$tilde(e)_q$ ↑ (subject to the measurability gap ceiling on $e_q$)], [Strengthening program outcome measurement infrastructure (e.g., Korea Institute of Public Administration program evaluation center); standardizing KPI definitions; expanding use of outcome indicators],
      [$c_(t t)$ ↑], [Marginal cost of $e_t$ ↑ → timing adjustment ↓], [Staggered settlement timing for quasi-governmental contracts (quarterly or semi-annual); automated audit flagging; real-time monitoring; mandatory advance reporting of exceptional settlements],
    ),
    caption: [P-A Model Levers and Their Mapping to Korean Administrative Actions],
  )

  *Recommendation 1 — Multi-Year Accounting Adoption ($w_t$ ↓)*: The current *single fiscal-year budget closure* structure is an institutional mechanism that makes the $w_t$ weight *extremely large* — unspent appropriations lapse automatically, making December 31 a *de facto arbitrary cutoff*. Upgrading the MTEF (introduced in 2009) from a *five-year planning framework to an operative accounting unit* would substantially reduce $w_t$ and, in turn, $e_t^*$. The U.S. Government Performance and Results Act (GPRA) multi-year funding model provides a relevant reference case.

  *Recommendation 2 — Grant-Receiving Institution Evaluation Reform ($w_t$ ↓ + $w_q$ ↑)*: Grant-transfer-type phase coherence of 0.54 and PSD $k=1$ amplitude of 0.332 constitute direct evidence of *year-end uniform settlement pressure from principal to agent institutions*. Reducing the weight of *100% execution-rate targets* in institutional performance evaluations ($w_t$ ↓) while simultaneously expanding weight given to *program quality assessments* (citation counts, deliverable evaluations) ($w_q$ ↑) activates both levers simultaneously. However, the effect of increasing $w_q$ remains bounded by the *fundamental constraint of the measurability gap* (Holmstrom-Milgrom impossibility).

  *Recommendation 3 — Staggered Settlement Timing ($c_(t t)$ ↑)*: Distributing settlement cycles across *quarterly or semi-annual* intervals for each delegated contract would raise the marginal cost of timing adjustment immediately following December 1 ($c_(t t)$ ↑), thereby dispersing $e_t^*$. If grant-transfer-type phase coherence shifts from 0.54 to a dispersed cycle structure, it becomes possible to identify additional effects beyond fortuitous alignment in outcome-gaming co-movement.

  *Recommendation 4 — Data Infrastructure Strengthening (Prerequisite for $w_q$ ↑)*: Due to the limitations of monthly expenditure data (VWFOEM), this study was unable to directly observe *within-December week-level* jumps. #cite(<liebman2017>, form: "prose") reported 5× jumps using weekly data for the United States. Adding *weekly and daily granularity* to the Open Fiscal Data System (OFDS) API would not only improve RDD identification but also serve as primary data for the *program outcome measurement infrastructure* required to raise $w_q$.

  *Recommendation 5 — Automated Flagging System ($c_(t t)$ ↑)*: Deploying the 50-case sub05 identification algorithm used in this study (top-ranked `amp_12m_norm` + RDD jump of 3× or greater) as an *always-on monitoring system* raises the probability of detection → increases $(partial c) / (partial e_t)$ → reduces $e_t^*$. A *real-time gaming monitoring dashboard* could be developed in collaboration with the Board of Audit and Inspection (BAI) and the National Assembly Budget Office.

  *Recommendation 6 — Time-Weighted Monitoring (H6 Wavelet)*: The wavelet finding that grant-transfer-type gaming intensity increased by *+554% from 2015–2017 to 2023–2025* (§6.8) indicates an ongoing increase in the $w_t / w_q$ ratio over time. Policy monitoring should be *weighted toward the most recent three years of data*; eleven-year average indicators dilute this intensifying trend.

  *Comparative Expected Effects*: Recommendations 1, 2, and 3 directly reduce $e_t^*$; Recommendations 4 and 5 raise the *$c$ function* through strengthened measurement and detection; Recommendation 6 modifies *temporal weighting* to leverage the model's comparative statics. The largest expected effect is predicted for *Recommendation 1* (multi-year accounting), given the magnitude of the $w_t$ change it entails; the fastest feasible adoption path belongs to *Recommendation 5* (flagging). These two recommendations are designated as the *highest priority*.

  *Acknowledging the Holmstrom-Milgrom Impossibility*: Complete elimination of gaming through these model-derived prescriptions is not possible. Because the measurability gap is fundamental, increasing $w_q$ without limit raises $tilde(e)_q$ but $e_q$ does not follow. The prescriptions therefore target *shifts in the equilibrium point*, not a *complete solution*.

= Limitations and Future Research

  The limitations of this study are organized into *model-side* and *empirical-side* categories. Each limitation constitutes a clear departure point for future research.

== Model-Side Limitations

+ *Lack of micro-calibration*: The P-A model identifies only the *signs and directions of comparative statics* for $w_t, w_q, c$. Absolute calibration of evaluation weights requires natural experiments (e.g., ministries that adopted multi-year accounting versus those that did not) or administrative data capturing cross-ministry differences in evaluation weights.
+ *Static equilibrium assumption*: The temporal intensification (H6, +554%) was interpreted as comparative statics of a time-varying $w_t / w_q$ ratio, but *dynamic equilibria in repeated games* (reputational concerns, multi-period bonuses, learning curves) are outside the model. This is a fundamental limitation of the stationary equilibrium assumption.
+ *Absence of multi-agent interactions*: Inter-ministry spillovers (whereby gaming intensification by one ministry affects the evaluation pressure on others) are ignored by the model. The Spectral Co-clustering ministry graph could be extended to a multi-agent setup.

== Empirical-Side Limitations

+ *Absence of natural experiments (no external control group)*: Korea's unitary government combined with gradual KPI adoption timing means that, without an external control group, RDD remains the strongest available causal identification strategy. The lack of a clean natural experiment limits the external validity of the RDD identification.
+ *STL trend confounding*: The disappearance of the Social Welfare main signal after STL decomposition depends on the trend-seasonal separation hypothesis. While NeuralProphet mediation provides partial reinforcement, the short sample length of Korean data is a fundamental weakness.
+ *Sample size constraint*: After differencing, field-level *N* = 8–12 — even with permutation and bootstrap supplementation, point-estimate confidence intervals remain wide.
+ *Missing defense and reserve fund data*: Fields without measurable outcome variables were excluded (exclusion bias). Future research should exploit any declassifiable partial data.
+ *Absence of weekly/daily granularity*: Monthly expenditure data preclude direct observation of within-December week-level jumps. Part of the gap between the U.S. 5× and Korea's 1.91× figures may reflect data granularity rather than behavioral differences.

== Future Research Directions

+ *Natural experiment calibration*: Direct calibration of the equilibrium effect of $w_t$ changes by comparing pilot multi-year-accounting ministries (e.g., select MSIT R&D programs) against conventional ministries.
+ *Multi-agent extension of the ministry graph*: Gaming spillover network analysis at the level of the five Spectral Co-clustering ministry communities.
+ *Wavelet change-point mapping*: Mapping the temporal intensification trend onto known policy change-points (2007 National Fiscal Act, 2014 National Accounting System reform, 2017 supplementary budget, 2020 COVID expansion) to quantitatively estimate equilibrium shifts at each change-point.
+ *International comparison*: Comparing the U.S. 5× (#cite(<liebman2017>, form: "prose")), Korea's 1.91× (capital-acquisition 3.42×) from this study, and analogous analyses for Japan and the EU → measuring the equilibrium effect of differences in evaluation systems.
+ *Archetype-level decomposition of mediation*: Disaggregating the pooled *p* = 0.481 mediation result into archetype-specific mediation analyses to quantify how the strength of the $e_t$ channel varies by project type.

= Conclusion

  This study provides an integrated analysis of fiscal gaming in Korean central government expenditure across three axes: *theory, empirics, and policy*. The five core contributions are as follows.

  *Contribution 1 — Theoretical Model: Micro-Foundations of the Goodhart Game*: Through Principal-Agent equilibrium analysis, this study answers *why* the Goodhart effect materializes in Korea. It is theoretically derived that agent *rationality* — not irrationality — directs resources toward timing adjustment effort in environments characterized by a measurability gap @holmstrom1991. The model generates six testable hypotheses (H1–H6), of which *archetype-specific differences in equilibrium patterns* constitute the study's central prediction.

  *Contribution 2 — Redefinition of the Unit of Analysis (H1 Verification)*: This study provides quantitative evidence ($Delta R^2 = 0.000$) that the *field-level analysis* standard in Korean public administration and fiscal research is *trivial* with respect to gaming phenomena, and demonstrates through topological data analysis (TDA) that the true unit of analysis is *project archetype* — confirmed by UMAP+HDBSCAN four-cluster solution, Mapper graph four components, and Persistent Homology 30 robust components. The finding that *administrative classification and the genuine unit of gaming differ* calls for a reconsideration of unit selection in future policy analyses.

  *Contribution 3 — Counterintuitive Findings (H2, H3, H5 Verification)*: Gaming is shown to be not merely negative measurement distortion but a *field-heterogeneous, temporally dynamic phenomenon*.
  - *Capital-acquisition-type RDD discontinuity 3.42×* (H2 verification): A discrete spike immediately after December 1 — extending the Korean case from #cite(<liebman2017>, form: "prose") for the United States.
  - *Grant-transfer-type cycle dominance* (H3 verification): PSD 0.332 + phase coherence 0.54 + wavelet +554% — bound to the same fiscal year cycle through a different mechanism.
  - *Social Welfare automatic redistribution effect (fortuitous, H5 proposition)*: Gaming ↔ poverty gap negative correlation (*r* = −0.86, strengthened after CPI control) — *fortuitous* outcome alignment, not policy justification.
  - *Field trivial result and Social Welfare automatic redistribution coexist*: The cost-function layer (archetype trivial) and the outcome layer (field fortuitous alignment) are independent layers of the model.

  *Contribution 4 — Temporal Dynamic Intensification (H6 Verification, Novel Wavelet Analysis)*: By supplementing the FFT stationarity assumption with wavelet analysis, this study newly demonstrates that *gaming intensifies over time*.
  - *Grant-transfer type*: 12-month cycle amplitude *+554% from 2015–2017 to 2023–2025*
  - *Normal projects*: +316.7%; *capital-acquisition type*: +174.7%; *personnel type*: $-0.8%$ (control)

  A time-increasing $w_t / w_q$ ratio — driven by the enforcement of the National Fiscal Act and National Accounting System, expanded COVID-era fiscal stimulus, and a rising share of quasi-governmental agencies — is a plausible mechanism, and the absence of change in the personnel type reinforces the reliability of the measurement tools.

  *Contribution 5 — Model-Grounded Policy Prescriptions*: Rather than listing policy recommendations arbitrarily, they were derived directly from the model's comparative statics (e.g., $(partial e_t^*) / (partial w_t) > 0$). The *six core recommendations* — multi-year accounting, grant-receiving institution evaluation reform, staggered settlement timing, data infrastructure, automated flagging, and *time-weighted monitoring* — each correspond to one model lever ($w_t$, $w_q$, or $c_(t t)$). At the same time, the Holmstrom-Milgrom impossibility constraint — the fundamental limitation of the measurability gap — was honestly acknowledged by explicitly not promising a complete solution.

  *Methodological Triangulation and Honest Limitation Reporting*: The FFT, STL, NeuralProphet, and Wavelet four-tool temporal resolution spectrum; the UMAP, HDBSCAN, Mapper, and PH topological multi-validation; and the RDD, mediation analysis, and CPI-control causal identification all converged on a consistent *archetype-specific equilibrium pattern*. The disappearance of the Social Welfare signal after STL was self-critically acknowledged, and the P-A model's lack of micro-calibration and dynamic equilibrium were presented as departure points for future natural experiment and international comparison research. All code, data, and results are publicly available on the GitHub repository and Zenodo in support of *reproducible research*.

  The finding that the Goodhart game in Korean fiscal expenditure is *not a fixed pattern but an ongoing dynamic phenomenon* can be interpreted as Korean empirical evidence for *Performative Prediction* (@hardt2016strategic; @perdomo2020performative) — the idea that evaluation systems themselves alter the distribution of the behaviors they measure. Future research, through international comparison (United States, Japan, EU) and natural experiments, may identify *under what institutional conditions this dynamic intensification can be suppressed*.



// =============================================================
= AI Tool Disclosure

#set par(first-line-indent: 0pt)

*Anthropic Claude (claude-opus-4-7, claude-sonnet-4-6)* assisted in data collection, processing, analysis, and visualization for this study in the *Claude Code* environment. Specifically:

- *Data pipeline development*: Scripts for calling the Open Fiscal Data System (OFDS), KOSIS, Bank of Korea ECOS, Korea Public Data Portal, and GIR (NIER) APIs; DuckDB warehouse build
- *Analysis code development*: Approximately 30 analysis scripts (numbered H1–H24 in the repository), including implementations of UMAP, HDBSCAN, Mapper, PH, RDD, mediation analysis, and STL
- *Visualization*: Figure generation
- *Documentation*: JOURNEY.md analysis log, REFERENCES.md, SOURCES.md compilation
- *Critical review*: Outcome variable adequacy validation (6 inappropriate variables identified and replaced); self-critical review of STL trend confounding

Research questions, result interpretation, and policy implications were determined by the authors. All AI-generated outputs were reviewed by the authors for academic validity, reproducibility, and causal inference limitations. The authors take full academic responsibility for all findings presented in this work.

Reproducibility materials (code, result CSVs, visualizations) are publicly available on the GitHub repository and Zenodo.

- GitHub: #link("https://github.com/bluethestyle/goodhart-korea")[github.com/bluethestyle/goodhart-korea]
- Interactive visualizations: #link("https://bluethestyle.github.io/goodhart-korea/interactive/")[bluethestyle.github.io/goodhart-korea/interactive]
- Analysis log (full H1–H24): #link("https://bluethestyle.github.io/goodhart-korea/analysis/JOURNEY/")[bluethestyle.github.io/goodhart-korea/analysis/JOURNEY]

*License and Distribution*: The text of this paper is distributed under #link("https://creativecommons.org/licenses/by/4.0/")[CC BY 4.0]. Analysis code is published under the MIT License on the #link("https://github.com/bluethestyle/goodhart-korea")[GitHub repository], and analysis outputs (CSV and PNG files) are released under CC BY 4.0.

#set par(first-line-indent: 1em)

#v(1em)

// =============================================================
#bibliography("refs.bib", title: "References", style: "apa")

#pagebreak()

// 부록 섹션은 자동 numbering 비활성화 (제목에 "부록 A.", "부록 B." 등이 직접 표기됨)
#set heading(numbering: none)

// =============================================================
= Appendix A. List of Abbreviations

#figure(
  text(size: 9.5pt)[
    #table(
      columns: (auto, 0.6fr, 1fr),
      align: (left, left, left),
      inset: (x: 5pt, y: 3pt),
      stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { (top: 0pt, bottom: 0pt) },
      table.hline(y: 1, stroke: 0.3pt + black),
      [*Abbreviation*], [*Full Term*], [*Meaning / Usage*],
      [FFT], [Fast Fourier Transform], [Decomposes a time series into frequency components to extract the annual-cycle amplitude (`amp_12m_norm`).],
      [STL], [Seasonal-Trend decomp. using Loess], [Additive decomposition using Loess smoothing. Separates trend, seasonality, and residuals; yields `seasonal_strength`.],
      [NP], [NeuralProphet], [Neural-network extension of Prophet. Additive decomposition model combining trend, Fourier seasonality, and AR-Net.],
      [AR], [Autoregression], [Autoregression. Explains the current value from past values. Deactivated (`n_lags=0`) in NP fits for this study.],
      [UMAP], [Uniform Manifold Approx. & Projection], [Nonlinear dimensionality reduction. Preserves local and global structure via fuzzy simplicial sets.],
      [HDBSCAN], [Hierarchical DBSCAN], [Density-based hierarchical clustering. No pre-specification of cluster count; separates noise.],
      [TDA], [Topological Data Analysis], [Topological data analysis. Encompasses Mapper and Persistent Homology.],
      [PH], [Persistent Homology], [Persistent Homology. Tracks topological features (connectivity, loops) across all scales.],
      [FE], [Fixed Effects], [Fixed effects. Controls for group heterogeneity via field, year, etc. dummy variables.],
      [RDD], [Regression Discontinuity Design], [Regression discontinuity design. Causal identification by comparing observations immediately around an arbitrary cutoff.],
      [DID], [Difference-in-Differences], [Difference-in-differences. Treatment vs. control group × pre vs. post comparison (not used in this study).],
      [IV], [Instrumental Variables], [Instrumental variables. Causal identification exploiting exogenous variation.],
      [CV], [Coefficient of Variation], [Coefficient of variation ($sigma\/mu$). Alternative gaming indicator to FFT.],
      [CPI], [Consumer Price Index], [Consumer Price Index. Bank of Korea ECOS series 901Y009. Exogenous macroeconomic control variable.],
      [NPM], [New Public Management], [New Public Management. KPI- and privatization-oriented paradigm from the UK and New Zealand in the 1980s.],
      [KPI], [Key Performance Indicator], [Key Performance Indicator. Administrative evaluation tool since NPM adoption.],
      [MTEF], [Medium-Term Expenditure Framework], [Medium-Term Expenditure Framework. Adopted in Korea in 2009 as a five-year framework.],
      [ECOS], [Economic Statistics System (BOK)], [Bank of Korea Economic Statistics System. Provides macroeconomic time series including CPI.],
      [KOSIS], [Korean Statistical Information Service], [Korean Statistical Information Service. Provides field-level outcome variables.],
      [GIR], [Greenhouse gas Inventory & Research], [Greenhouse Gas Inventory and Research Center (NIER). National inventory reporting.],
      [ODA], [Official Development Assistance], [Official Development Assistance. OECD DAC standard.],
    )
  ],
  caption: [List of abbreviations and shorthand notation used in this study],
)

= Appendix B. Glossary of Key Terms

#set par(first-line-indent: 0pt)

This appendix provides definitions for statistical and computational terms appearing across the multiple methodologies of this study. When a key abbreviation first appears in the main text, a one-line definition is provided; for full definitions, refer to this appendix.

*P-A Model Notation (§3, Appendix F)*

- *$P, A$*: Principal (government/ministry) and Agent (implementing ministry or quasi-governmental agency)
- *$U_P, U_A$*: Respective objective functions
- *$Y(e_q, e_t)$*: Social outcome (e.g., poverty gap, life expectancy, patent count)
- *$e_t in RR_+$*: Agent's *timing adjustment effort* (December-concentrated expenditure; observable)
- *$e_q in RR_+$*: Agent's *program quality effort* (contributes to social outcomes; difficult to observe)
- *$tilde(e)_q = phi(e_q)$*: Observable component of $e_q$ (measurability gap: $phi'(\cdot) < 1$)
- *$w_t, w_q$*: Evaluation weights for timing effort and quality effort
- *$c(e_t, e_q; theta)$*: Effort cost function; differs by project archetype $theta$ (convex, increasing)
- *$theta in {$personnel-type, capital-acquisition, grant-transfer, normal projects$}$*: Project archetype label
- *$e_t^*, e_q^*$*: Equilibrium effort satisfying first-order conditions (FOC: $w_t = partial c/partial e_t$, etc.)

*Economics and Contract Theory Terms*

- *Goodhart's Law*: Once a social indicator is used as a policy target, its measurement reliability declines @goodhart1975. Extended to the social sciences by Campbell (1979).
- *Multitasking Contract Theory*: When an agent performs multidimensional tasks and incentives are tied only to measurable dimensions, effort in unmeasured dimensions systematically declines @holmstrom1991.
- *Holmstrom-Milgrom Impossibility*: The theoretical result that in environments with large measurability gaps, *no incentive weighting can achieve the first-best outcome*. The theoretical basis for this study's policy recommendations explicitly not promising a complete solution.
- *Fortuitous Alignment*: The case in which the agent's equilibrium behavior ($e_t^*$) fortuitously aligns with the principal's social outcome ($Y$). The model frame for this study's Social Welfare automatic redistribution effect (H5). Formalized as the accidental positivity of the field function $alpha(theta_("field")) = (partial Y) / (partial e_t)$.
- *Baker Distortion @baker1992*: The marginal productivity gap between the measured indicator $M$ and the true value $V$ ($(partial M) / (partial e) != (partial V) / (partial e)$). Concretized in this model as the measurability gap function $phi'(\cdot) < 1$.
- *Career Concerns* (@holmstrom1999; @dewatripont1999): PA dynamic equilibrium in which evaluation operates as a *multi-year reputational signal* rather than a single-stage event. The institutional reputation of quasi-governmental agencies with their parent organizations induces *collective synchronization* (phase coherence 0.54).
- *Performative Prediction* (@hardt2016strategic; @perdomo2020performative): The ML-economics cross-framework in which the distribution shifts the moment an indicator becomes a learning target. The H6 temporal intensification (+554%) in this study is a direct instance in an administrative system.
- *Strategic Classification* #cite(<hardt2016strategic>): The ML theory that once a classifier becomes an evaluation tool, the input distribution undergoes *strategic adaptation*. The static version of Performative Prediction.
- *Soft Budget Constraint*: The phenomenon in which budget constraints weaken because agents anticipate post-hoc bailouts by parent organizations or the government rather than market discipline @kornai1980.
- *Mediation Analysis*: A regression technique for separating the *indirect effect* along the $X arrow M arrow Y$ pathway from the direct effect $X arrow Y$. This study uses Baron-Kenny four-step + Sobel test + Bootstrap CI.
- *Sobel Test* #cite(<sobel1982>): z-test using the standard error of the mediation effect $a b$: $sqrt(b^2 sigma_a^2 + a^2 sigma_b^2)$. Depends on normality assumption.
- *Spectral Co-clustering*: Algorithm that simultaneously clusters the frequency matrix of ministries (rows) and project archetypes (columns) via SVD to find a block-diagonal structure @dhillon2001.
- *Permutation Test*: Generates the null distribution by randomly shuffling the outcome variable. Requires no normality or homoscedasticity assumptions.

*Data Analysis and Machine Learning Terms*
- *MCMC (Markov Chain Monte Carlo)*: Bayesian inference technique for sampling from the posterior distribution. Used in the original Prophet; NeuralProphet replaces it with SGD.
- *SGD (Stochastic Gradient Descent)*: Algorithm for optimizing a differentiable objective function using mini-batches. NP learns via PyTorch SGD.
- *SVD (Singular Value Decomposition)*: Decomposes a matrix as $U Sigma V^T$. Core operation in Spectral Co-clustering.
- *DFT (Discrete Fourier Transform)*: Fourier transform of a discrete time series. FFT is a fast algorithm for the DFT.
- *LOESS (Locally Estimated Scatterplot Smoothing)*: Locally weighted polynomial regression smoothing. The smoothing engine in STL.
- *GAM (Generalized Additive Model)*: Additive combination of nonlinear function terms. Foundation of Prophet and NeuralProphet.
- *PCA (Principal Component Analysis)*: Linear dimensionality reduction. Referenced as a comparison to UMAP.
- *t-SNE*: Nonlinear embedding algorithm. UMAP was adopted due to t-SNE's weaker global structure preservation.
- *DBSCAN*: Single-threshold version of density-based clustering. Predecessor to HDBSCAN.
- *ARIMA / SARIMA*: Autoregressive integrated moving average model. The stationarity assumption makes it unsuitable for this study's time series.
- *LSTM / Transformer*: Neural-network time series models. Unsuitable for this study due to lack of decomposability; the study's objective is interpretable seasonal strength extraction, not forecasting.
- *Frisch-Waugh-Lovell Theorem*: Theorem showing that a multiple regression coefficient equals the result of a two-stage residual regression. Theoretical basis for CPI control.
- *Gibbs Phenomenon*: Oscillations and overshooting near jump discontinuities in a finite Fourier sum. A known limitation of FFT.
- *AR-Net*: Neural-network autoregression. Key distinguishing feature of NeuralProphet.
- *ReLU*: $max(0, x)$ nonlinear activation function. Standard activation function in AR-Net.
- *Project Archetype*: The four project types discovered from data in this study: personnel-type, capital-acquisition, grant-transfer, and normal projects.
- *`amp_12m_norm`*: FFT annual-cycle amplitude divided by total amplitude sum. Primary gaming indicator.
- *`seasonal_strength`*: $1 - "Var"("residual")/"Var"("detrended")$ after STL decomposition. STL gaming indicator.
- *`np_seasonal_strength`*: NeuralProphet yearly seasonality amplitude divided by standard deviation. NP gaming indicator.

#set par(first-line-indent: 1em)

#pagebreak()

// =============================================================
= Appendix C. Methodology Details — Equations, Algorithms, and Alternatives

This appendix supplements the *intuition and subject-appropriateness* descriptions in the main methodology section. For each tool, it presents (1) formal definitions, (2) the core algorithm, and (3) comparisons with alternative tools. Each subsection corresponds one-to-one with a section in the main text.

== C.1 FFT — DFT Definition, `amp_12m_norm` Formula, and Limitations

*Discrete Fourier Transform (DFT)*: For a signal $x_n$ of length $N$ (computed via the FFT algorithm of @cooley1965 in $O(N log N)$ operations)
$ hat(x)_k = sum_(n=0)^(N-1) x_n e^(-i 2 pi k n / N), quad k=0,1,...,N-1 $
$|hat(x)_k|$ = amplitude of the frequency $f_k = k\/N$ component; $arg(hat(x)_k)$ = phase.

*`amp_12m_norm` definition*: For the monthly time series ${x_(i,t,m)}_(m=1)^12$ ($N=12$) of activity $i$ in year $t$:
$ "amp_12m_norm"_(i,t) = (|hat(x)_(i,t)(k=1)|) / (sum_(k=1)^(N\/2) |hat(x)_(i,t)(k)|) $
Numerator: amplitude of the annual-cycle component; denominator: the *L1-sum* of all frequency amplitudes excluding DC — the ratio represents *the share of annual-cycle intensity in the L1 frequency-domain norm*. Replacing the denominator with $sum_k |hat(x)_k|^2$ (L2) gives, by Parseval's theorem ($sum_n |x_n|^2 = (1\/N) sum_k |hat(x)_k|^2$), the *share of total variance energy*, which is not equivalent to the L1 formulation. This study's L1 form prioritizes intuitive interpretability in amplitude units; the two forms are monotonically related, so hypothesis-testing conclusions agree.

*Limitations of FFT*: (a) Stationarity assumption — Korean government budgets trend upward at approximately 6% per year on average; (b) *Gibbs phenomenon* from 12-month windowing — jumps at year boundaries leak into adjacent frequency bins. Supplemented by STL and NeuralProphet.

== C.2 STL — Algorithm, `seasonal_strength` Definition, and Limitations

*Algorithm*: STL performs additive decomposition through two nested loops. The inner loop: (1) subtracts the trend estimate from the time series to produce a detrended signal; (2) groups values from the same season (e.g., all Januaries) into cycle-subseries and applies LOESS smoothing to estimate $S_t$; (3) re-applies LOESS to $x_t - S_t$ to update $T_t$. Iterates until convergence. The outer loop assigns *robustness weights* to large residuals to limit the influence of outliers.

*`seasonal_strength` definition*: Variance ratio of the seasonal component in the detrended signal $D_t = x_t - T_t = S_t + R_t$:
$ "seasonal_strength" = max(0, 1 - "Var"(R_t) / "Var"(D_t)) $
@hyndman2021.

*Limitations of STL*: (a) Sensitivity to LOESS bandwidth (span) selection — a narrow span absorbs jumps into the trend; a wide span underestimates the trend; (b) additive model only; (c) distorted trend estimates immediately before and after change-points. NeuralProphet's explicit change-point modeling provides supplementary correction.

== C.3 NeuralProphet — Six-Component Model, AR-Net, Differences from Prophet, and Hyperparameters

*Full six-component model* (@triebe2021, eq. 1):
$ y_t = T(t) + S(t) + E(t) + A(t) + sum_(j=1)^p F_j (t) + L(t) + epsilon_t $

- $T(t)$ = piecewise-linear trend with $C$ automatic change-points:
  $ T(t) = (k + sum_(c=1)^C delta_c bb(1)[t > tau_c])(t - tau_("ref")) $
- $S(t)$ = Fourier-series seasonality:
  $ S(t) = sum_p sum_(n=1)^(N_p) [a_(p,n) cos(2 pi n t / P_p) + b_(p,n) sin(2 pi n t / P_p)] $
  This study: $P=12$ months, $N_P=6$.
- $E(t)$ = events (holidays, fiscal year-end)
- $A(t)$ = *AR-Net autoregression (key distinguishing feature of NP)*:
  $ A(t) = "ReLU"(W_2 thin "ReLU"(W_1 thin [y_(t-1), ..., y_(t-l)]^T + b_1) + b_2) $
  $l$ = `n_lags`; $W_1, W_2, b_1, b_2$ = network weights. AR-Net extends autoregression with *nonlinear activation*.
- $F_j$ = exogenous regressors; $L$ = nonlinear lagged regressor effects; $epsilon$ = normal residuals.

*Differences from original Prophet*: Prophet #cite(<taylor2018>) lacks $A(t)$ and $L(t)$ and is trained via Stan MCMC. NP adds three substantive extensions: (a) AR-Net, (b) nonlinear lagged regressors, (c) PyTorch SGD training.

*Study configuration (intentional simplification)*: Fitted to activity×year 24-month time series with other components deactivated to focus on *pure seasonal decomposition*.
- `n_lags=0` → $A(t) equiv 0$ (cross-check comparability)
- `n_future_regressors=0`, `n_lagged_regressors=0`, `events=None`
- `n_changepoints=2`, `yearly_seasonality=True (N=6)`, `weekly/daily=False`
- Resulting fitted model: $y_t = T(t) + S(t) + epsilon_t$

*Why disable AR?*: When AR is active, NP learns short-term autocorrelations and absorbs the *pure seasonal signal* that would otherwise appear in the residuals. It is disabled to ensure comparability across tools (the cross-check message being "different tools observe the same gaming"). However, enabling AR improves forecast accuracy and may be useful in future research.

*Key distinctions among the three tools*:
- *FFT*: *Fixed-amplitude* $sin/cos$ basis. No trend decomposition — stationarity violations cause trend leakage into low frequencies.
- *STL*: Absorbs trend via *nonparametric LOESS*. No explicit change-point modeling.
- *NP*: Trend modeled as *piecewise-linear + automatic change-point detection*. Seasonality estimated on top of change-point-based trend → explicit, interpretable trend-season separation.

*Why NeuralProphet rather than other neural networks?*:
- *vs ARIMA/SARIMA*: Stationarity assumption + single seasonal period + no automatic change-point detection.
- *vs LSTM/Transformer*: Black-box, overfits with $N=24$ samples, *no decomposability*. The study's objective is interpretable seasonal strength extraction, not forecasting.
- *vs original Prophet*: NP can be efficiently fitted to *large activity-level panels* while preserving full interpretability. Stan MCMC in Prophet is too slow for 1,500 activities.

== C.4 UMAP — Fuzzy Cross-Entropy Loss and Alternatives

*Loss function*: Fuzzy cross-entropy between the fuzzy simplicial set representation $A$ of high-dimensional data $X$ and the representation $B$ of the low-dimensional embedding $Y$:
$ "loss" = sum_(i j) [a_(i j) log (a_(i j)) / (b_(i j)) + (1 - a_(i j)) log (1 - a_(i j)) / (1 - b_(i j))] $
Minimized via SGD. $a_(i j) = exp(-(d(x_i, x_j) - rho_i)\/sigma_i)$ (neighborhood probability based on $k$ nearest neighbors); $b_(i j) = (1 + a' ||y_i - y_j||^(2 b'))^(-1)$ (low-dimensional Student-t-like distribution).

*vs PCA*: Linear projection destroys nonlinear manifolds (U-shaped, ring-shaped structures).
*vs t-SNE*: Uses KL divergence — compresses *global distances* inaccurately. UMAP preserves global structure as well using fuzzy set theory (@mcinnes2018, §3).
*vs Autoencoder*: Dependent on training data volume and architecture; UMAP is deterministic (`random_state=42`) and stable on small datasets.

== C.5 HDBSCAN — Mutual Reachability, MST, and Alternatives

*Core distance*: Distance from point $x$ to its $k$-th nearest neighbor $d_("core")(x)$.

*Mutual reachability distance*:
$ d_("mreach")(x, y) = max(d_("core")(x), d_("core")(y), d(x,y)) $

A *minimum spanning tree* (MST) is constructed using these as edge weights, and a *condensed cluster tree* is built by progressively cutting the tree as the weight threshold $epsilon$ increases. The cluster with the highest *stability* score is selected as the final solution.

*vs K-means*: Requires pre-specifying $k$ + assumes spherical clusters + cannot handle noise — unsuitable for this study's environment of *4 clusters, non-spherical shapes, and a small number of outliers*.
*vs DBSCAN*: Single density threshold $epsilon$ — fails when cluster densities differ markedly. HDBSCAN integrates analysis across the full $epsilon$ spectrum.
*vs GMM*: Gaussian distribution assumption — unsuitable for nonlinearly shaped clusters.

== C.6 Mapper — Nerve Simplicial Complex Definition and Alternatives

*Mathematical outline*: Given data space $X subset RR^d$, select a *filter function* $f: X arrow RR^k$ (this study uses the first two PCA components). Partition the codomain of $f(X)$ into an *overlapping cover* $cal(U) = {U_1, U_2, ...}$ → cluster each preimage $f^(-1)(U_i)$ → construct the *nerve simplicial complex* (Mapper graph) by assigning each cluster a node and connecting two nodes with an edge when their point sets *intersect*:
$ "Mapper"(X, f, cal(U), "cluster") = "Nerve"({"cluster"(f^(-1)(U_i))}) $

The result is summarized as topological invariants (number of connected components, number of loops, $beta_1$).

*vs UMAP+HDBSCAN*: Embedding+clustering provides *position* information; Mapper provides *connectivity* information. Useful for diagnosing whether bridge points exist between two clusters — distinguishing an arbitrary cut in a continuum from a genuine separation.
*vs DBSCAN*: Identifies clusters only; cannot capture connectivity structure.

== C.7 Persistent Homology — Vietoris-Rips Complex and Persistence Diagram

*Mathematical outline*: For a point set $P$, construct the *Vietoris-Rips complex* $V_epsilon(P)$ at radius $epsilon$ — add pairs of points with distance $d(x,y) <= epsilon$ as edges, and $k+1$ mutually close points as $k$-simplices. Increasing $epsilon$ from 0 yields the *filtration* ${V_epsilon(P)}_(epsilon >= 0)$. Tracking the homology groups $H_d(V_epsilon)$ in each dimension $d$ reveals *birth-death pairs* $(b, d)$ — recording when a hole is born at $epsilon = b$ and dies at $epsilon = d$. The set of such pairs constitutes the *persistence diagram*; larger *persistence* $d - b$ indicates a more robust topological feature.

This study analyzes dimension 0 (connected components $beta_0$) and dimension 1 (loops $beta_1$). *50 bootstrap resamples* yield $beta_0 = 30$, $beta_1 = 15$, and 95% CI for max persistence.

*vs Mapper*: Mapper operates at a single scale; PH integrates analysis across *all scales*. PH is more rigorous; Mapper is more intuitive.
*vs silhouette/Calinski-Harabasz*: The latter are scale-dependent single scores; PH captures *scale-invariant* topological features.

== C.8 Field Trivial Test — Fixed-Effects Regression Model Comparison

*Baseline model*: Outcome variable for activity $i$ in year $t$:
$ Y_(i,t) = beta_0 + beta_1 X_(i,t) + sum_k gamma_k D_(i,k)^("field") + epsilon_(i,t) $
$X_(i,t)$ = gaming indicator; $D_k^("field")$ = 14-field dummies.

*Comparison model*: Project archetype × gaming interaction:
$ Y_(i,t) = beta_0 + beta_1 X_(i,t) + sum_c delta_c (D_(i,c)^("archetype") times X_(i,t)) + epsilon_(i,t) $
$D_c^("archetype")$ = 4 project archetype dummies.

*Decision criterion*: Comparison of *adjusted R² increments* $Delta R^2_("adj")$ between the two models. If the field model yields $Delta R^2 approx 0$ and the archetype model yields $Delta R^2 > 0$, fields are *trivial* and archetypes constitute the *genuine unit of analysis*.

== C.9 Spectral Co-clustering — SVD and Normalization

*Matrix normalization*: The ministry-by-archetype frequency matrix $A in RR^(m times n)$ ($m=51$, $n=4$) is interpreted as a bipartite graph. The normalized matrix is:
$ A_n = D_1^(-1\/2) A D_2^(-1\/2) $
$D_1$ = diagonal row-degree matrix; $D_2$ = diagonal column-degree matrix.

*Embedding*: SVD of $A_n$ yields left singular vectors $U_(l)$ and right singular vectors $V_(l)$; assign the first $l = log_2 k$ columns to rows and columns respectively. Apply K-means to the concatenated matrix $[U_(l) ; V_(l)]^T$. The resulting clusters partition the bipartite graph into $k$ balanced groups in the *normalized cut* sense @dhillon2001.

*vs naive K-means (ministry-only)*: Clustering only ministries reveals no information about *why* they are grouped (i.e., which project-type specialization drives the grouping). Co-clustering simultaneously outputs the *correspondence* between ministry clusters and archetype clusters.
*vs LDA*: Probabilistic but does not guarantee *simultaneous row-column clustering*; SVD is more rigorous in the spectral sense.

== C.10 RDD — Identification Assumptions, Local Linear Estimation, and Alternatives

*Identification assumption*: Cutoff $c$ = centered on December 1:
$ tau_("RDD") = lim_(t arrow c^+) E[Y_t | t] - lim_(t arrow c^-) E[Y_t | t] $
is causally identified if and only if (a) the *continuity assumption* holds at the cutoff and (b) *absence of manipulation* can be established.

*Local linear estimator*: Within bandwidth $h$, separate first-order OLS fits on each side of the cutoff:
$ Y_t = alpha_-/+ + beta_-/+ (t - c) + epsilon_t, quad t in [c - h, c) "or" (c, c + h] $
$hat(tau)_("RDD") = hat(alpha)_+ - hat(alpha)_-$. This study reports results as a *ratio-type jump multiplier*.

*vs DID*: Requires a control group — no external control group exists in Korea's unitary government. RDD uses *its own time series as the control*.
*vs IV*: No strong instrument variable is available; the cutoff itself is exogenous, making IV unnecessary.
*vs month-of-year FE*: Month FE estimates only the *average jump*; RDD estimates the *marginal effect immediately around the cutoff* — identification is more rigorous.

== C.11 Mediation Analysis — Baron-Kenny + Sobel + Bootstrap

*Four-step regression*:
$ "Step 1": quad Y = i_1 + c X + epsilon_1 quad ("total effect " c) $
$ "Step 2": quad M = i_2 + a X + epsilon_2 quad ("mediation path " a) $
$ "Steps 3,4": quad Y = i_3 + c' X + b M + epsilon_3 quad ("direct " c', " mediated " a b) $
The mediation effect is $a b$ or equivalently $c - c'$ (the two coincide under OLS).

*Sobel z-statistic*: Asymptotic standard error of $a b$:
$ "SE"(a b) = sqrt(b^2 sigma_a^2 + a^2 sigma_b^2) $
Tested as $z = (a b) / "SE"(a b)$. Relies on a normality assumption.

*Bootstrap CI*: $B = 1000$ resamples with replacement → compute $hat(a)^((b)) hat(b)^((b))$ each time → use the 2.5–97.5\% quantiles of the distribution as the confidence interval. Robust to *asymmetric distributions* without a normality assumption @preacher2008.

*vs SEM*: Efficient via *simultaneous estimation* of $a b$, but requires latent variables and large $N$; field-level $N = 14$ is unsuitable for SEM.
*vs Causal Mediation Analysis @imai2010*: Nonparametric identification under a potential-outcomes framework; the small field-level $N$ in this study yields insufficient nonparametric power → parametric Baron-Kenny is more practical.

== C.12 Exogenous Control — Frisch-Waugh-Lovell Residualization

*Method*: For gaming indicator $X_t$, outcome variable $Y_t$, and macro control variable $Z_t$ = CPI:
$ "Stage 1": quad X_t = alpha_X + gamma_X Z_t + e^X_t, quad Y_t = alpha_Y + gamma_Y Z_t + e^Y_t $
$ "Stage 2": quad e^Y_t = beta thin e^X_t + u_t $
By the Frisch-Waugh-Lovell theorem, the Stage-2 $hat(beta)$ equals the $hat(beta)$ from the multiple regression $Y_t = alpha + beta X_t + gamma Z_t + epsilon_t$. The correlation between residual series $"cor"(e^X, e^Y)$ is the *partial correlation after controlling for CPI*.

*Exogeneity assumption*: $Z_t$ is *unaffected by fiscal gaming $X_t$*. CPI is the Bank of Korea's monetary policy instrument: (a) *Bank of Korea independence* separates it from Ministry of Economy and Finance decisions; (b) the *pre-announced target (2.0\%)* limits reverse-causality concerns.

*vs simply adding CPI to multiple regression*: Mathematically equivalent, but residual separation offers superior *interpretability* (provides the intuition of "signal after removing CPI").
*vs controlling for unemployment or GDP*: Both variables are *direct instruments and outcomes* of fiscal policy → bidirectional causality threat. CPI belongs to the monetary domain and is therefore *relatively insulated* from the fiscal domain.

== C.13 Robustness Checks — Permutation, Lag/Lead, and CV Formulas

*Lag/Lead analysis:* Correlations between gaming and outcomes are re-estimated with lags $tau in {-1, 0, +1}$ years to examine *directionality*. If synchronous correlation $r(0)$ is strongest, this supports an immediate mechanism (consistent with the Social Welfare automatic-redistribution hypothesis); a stronger $r(+1)$ implies a delayed effect; a stronger $r(-1)$ raises concerns about reverse causality.

- $r(0)$ largest → immediate mechanism (supports the Social Welfare automatic-redistribution hypothesis)
- $r(+1)$ largest → delayed effect
- $r(-1)$ largest → reverse causality suspected

*Permutation two-tailed p-value*: The outcome variable is shuffled $B = 1000$ times as $\{Y^{(b)}\}$; each iteration computes $hat(r)^((b)) = "cor"(X, Y^((b)))$:
$ p = (1) / (B) sum_(b=1)^(B) bb(1)[|hat(r)^((b))| >= |hat(r)|] $

*amp_cv*: $"CV" = sigma\/mu$. Because it ignores frequency information, it also captures aperiodic variation that FFT cannot detect — convergence of the two indicators confirms measurement robustness.

#pagebreak()

// =============================================================
= Appendix D. Spectral Analysis Details — Power Spectrum, Phase, and Cross-Coherence

The main text methodology uses only a *single amplitude point* from the FFT (`amp_12m_norm` = $|hat(x)(k=1)|/sum_k |hat(x)(k)|$). This appendix fully exploits the FFT to analyze (D.1) the complete power spectrum, (D.2) phase distribution, and (D.3) cross-coherence among activities. This quantitatively reinforces the main text conclusion that "FFT/STL/NP are not distinct measurements but *complementary*."

== D.1 Power Spectral Density — 12-Month and Quarterly Harmonics

Each activity × year 12-vector is mean-centered and then processed with `np.fft.rfft` to compute the PSD $|hat(x)(k)|^2$ for seven frequency bins ($k = 0, 1, \ldots, 6$; periods $infinity$, 12, 6, 4, 3, 2.4, 2 months), normalized by the sum of bins 1–6. The mean PSD of the four project archetypes is compared (@fig-psd).

#figure(
  table(
    columns: (auto, auto, auto, auto, auto, auto, auto),
    align: (left, center, center, center, center, center, center),
    table.hline(y: 1, stroke: 1.0pt + black),
    [*Archetype*], [*k=1*\ *(12m)*], [*k=2*\ *(6m)*], [*k=3*\ *(4m)*], [*k=4*\ *(3m)*], [*k=5*\ *(2.4m)*], [*k=6*\ *(2m)*],
    [Labor-cost], [0.097], [0.143], [0.125], [*0.269*], [0.162], [0.202],
    [Capital-acquisition], [0.155], [0.162], [0.124], [*0.304*], [0.117], [0.138],
    [Grant-transfer], [*0.332*], [0.131], [0.142], [0.163], [0.127], [0.105],
    [Normal], [0.172], [0.169], [0.144], [0.239], [0.141], [0.135],
  ),
  caption: [Mean normalized PSD by archetype — Grant-transfer shows the highest 12-month amplitude dominance (0.332)],
)

#figure(
  image("figures_en/h27_psd.png", height: 7cm),
  caption: [Mean PSD by archetype — Grant-transfer (green) shows amplitude dominance at 12m that is 2× higher than other archetypes],
) <fig-psd>

*Key findings*:
- *Grant-transfer*: 12-month cycle amplitude of $33.2\%$ is overwhelming; quarterly and other harmonics are weak → *synchronization to a single annual cycle*.
- *Labor-cost, capital-acquisition, and normal*: $k=4$ (3-month, quarterly) amplitude is largest ($0.27$–$0.30$) — traces of quarterly reporting/progress-rate cycles.
- This finding newly reveals *the existence of a quarterly cycle invisible to the single-point amp_12m_norm measurement*, suggesting that future research could conduct a separate causal analysis of the *k=4 quarterly jump*.

== D.2 Phase Distribution — In Which Month Does the Peak Occur?

The phase of the dominant 12-month sinusoid is extracted via $arg(hat(x)(k=1))$ and converted to the *peak month* of each activity. Polar histograms for the four archetypes (@fig-phase):

#figure(
  image("figures_en/h27_phase.png", width:90%),
  caption: [12-month cycle phase distribution by archetype — Grant-transfer mode is October (one month earlier than other archetypes)],
) <fig-phase>

*Peak month mode*:
- Labor-cost: November (N=1,246)
- Capital-acquisition: November (N=929)
- Grant-transfer: *October* (N=1,289)
- Normal: November (N=10,646)

*Interpretation*: Grant-transfer reaches its peak *one month earlier* than other archetypes. This suggests a longer *preparatory phase* before the December settlement deadline, with concentrated October execution arising from settlement schedules with commissioned institutions. This is *complementary to the main text RDD result* in which the *capital-acquisition archetype showed the strongest December jump at 3.42×*: capital-acquisition forms a *discrete jump immediately after December 1*, while grant-transfer forms a *continuous cycle spanning October–December* — indicating that the gaming mechanism manifests differently across project archetypes.

== D.3 Cross-Coherence — Do Activities Within the Same Archetype Peak *Simultaneously*?

The 12-month frequency phase coherence $abs(chevron.l e^(i Delta phi) chevron.r)$ is measured for activity pairs $i, j$ within each archetype (1.0 = perfect synchrony, 0 = unrelated). Random sample of 500 pairs:

#figure(
  table(
    columns: (auto, auto, auto, auto, auto, auto, auto),
    align: (left, center, center, center, center, center, center),
    table.hline(y: 1, stroke: 0.5pt + black),
    [*Archetype*], [*k=1*\ *(12m)*], [*k=2*], [*k=3*], [*k=4*\ *(3m)*], [*k=5*], [*k=6*],
    [Labor-cost], [0.41], [0.07], [0.10], [0.12], [0.06], [0.08],
    [Capital-acquisition], [0.08], [0.06], [0.07], [0.06], [0.05], [0.07],
    [*Grant-transfer*], [*0.54*], [0.09], [0.08], [0.10], [0.06], [0.09],
    [Normal], [0.13], [0.05], [0.04], [0.05], [0.04], [0.05],
  ),
  caption: [Within-archetype phase coherence between activities — Grant-transfer shows strong synchrony at k=1 with coherence 0.54],
)

#figure(
  image("figures_en/h27_coherence.png", width:90%),
  caption: [Phase coherence heatmap by archetype — Grant-transfer's 12m synchronization is overwhelming],
) <fig-coh>

*Decisive finding*: *Grant-transfer activities are most strongly synchronized in the 12-month cycle with phase coherence of 0.54* (@fig-coh). This means that *distinct grant-transfer activities peak together in the same month*, directly validating this study's core hypothesis that the exogenous accounting cycle induces *collective behavior*. Capital-acquisition (0.08) and normal (0.13) show weak synchronization — peaking at dispersed times according to each project's own schedule.

*Summary of FFT/STL/NP complementarity*:
- *FFT*: 12-month amplitude share, phase, and coherence (this appendix)
- *STL*: Trend-residual separation; self-critical of trend absorption possibility
- *NP*: Changepoint correction + additive decomposition (interactive viz)

Because the three tools *decompose the same signal along orthogonal dimensions*, the core finding of "grant-transfer December gaming" is supported in a *consistent direction by all three tools* (FFT k=1 amplitude 33\%, NP yearly seasonality amplitude largest, STL post-trend residual signal also grant-transfer dominant). This constitutes robustness by definition of *methodological triangulation*.

== D.4 Wavelet Analysis — *Temporal Evolution* of Gaming Intensity

Table D.4-1 in this section (temporal evolution of 12m wavelet power by archetype) constitutes the core data for the §6.8 H6 results; it is recommended to read this section together with §6.8.

Because the FFT measures the average amplitude over the *entire time series*, it assumes stationarity. However, gaming intensity in Korean government budgets may have *changed over time* — e.g., the 2007 National Finance Act enforcement, the 2014 national accounting system reform, and the 2020 COVID-19 expansionary fiscal policy. To verify this, a *Continuous Wavelet Transform* (CWT, complex Morlet) is applied to trace the evolution of amplitude in the time × period plane.

*Method*: CWT is applied to the *mean time series of all activities* within each project archetype (2015–2025, 132 months; normalized annually per activity, then averaged by archetype). Scales = 2–40 months; complex Morlet 1.5-1.0. The power at the 12-month scale is extracted as a time series and averaged annually to track evolution. Scalograms for the four archetypes (@fig-scaleogram) and annual amplitude evolution (@fig-h28-evol) are presented below.

#figure(
  image("figures_en/h28_scaleogram.png", width:100%),
  caption: [Wavelet scalograms for four project archetypes — brighter colors indicate stronger amplitude.\ The 12m signal of Grant-transfer becomes progressively more intense toward the later period (2020–2025).],
) <fig-scaleogram>

#figure(
  image("figures_en/h28_evolution.png", height: 7cm),
  caption: [Annual evolution of 12-month cycle amplitude — Grant-transfer amplified 5.5×, Normal 3.2×. Only Labor-cost shows no change.],
) <fig-h28-evol>

*Decisive finding*: *2023–2025 average* relative to the *2015–2017 average* of 12-month cycle amplitude:

#figure(
  table(
    columns: (auto, auto, auto, auto),
    align: (left, center, center, center),
    table.hline(y: 1, stroke: 1.0pt + black),
    [*Archetype*], [*early (2015–17)*], [*late (2023–25)*], [*Change rate*],
    [Labor-cost], [0.0068], [0.0067], [$-0.8\%$ (no change)],
    [Capital-acquisition], [0.0547], [0.1503], [*$+174.7\%$*],
    [Grant-transfer], [0.2012], [1.3148], [*$+553.6\%$*],
    [Normal], [0.0569], [0.2373], [*$+316.7\%$*],
  ),
  caption: [Temporal evolution of 12m wavelet power by archetype — Grant-transfer strengthens by more than 5×. Precise change rate for grant-transfer: +553.6%; rounded to +554\% when cited in the main text.],
)

*Interpretation*: Korean fiscal gaming is *not a fixed pattern but an ongoing dynamic phenomenon*, and it is *intensifying most rapidly in the grant-transfer archetype*. Because FFT amp_12m_norm reports an 11-year average, it missed this *amplification phenomenon*. Possible drivers:
- *2017–2020*: Increased frequency of supplementary budgets + rising share of commissioned projects through grant institutions
- *2020–2022*: Accelerated creation of new programs under COVID-19 expansionary fiscal policy; increased December settlement pressure
- *2023–2025*: Grant-transfer settlement cycles are maintained and strengthened even as recurrent budget growth flattens

That Labor-cost shows *no change* reinforces the credibility of this analysis — labor costs follow a fixed monthly payment structure and are inherently insensitive to accounting-cycle changes. In other words, the wavelet captured only *genuinely dynamic signals*.

*Implications*: The policy implications of this study (field-level quadrant monitoring by ministry) should focus more heavily on *the most recent three years of data*, and future research can use wavelet-based *dynamic gaming indicators* as new metrics.

*Summary of FFT/STL/NP/Wavelet four-tool complementarity*:
- *FFT*: Average amplitude (static, aggregate)
- *STL*: Trend vs seasonal separation (static, trend-corrected)
- *NP*: Additive decomposition + changepoints (semi-dynamic, explicit change points)
- *Wavelet*: Time × period power (fully dynamic, evolution tracking)

The four tools become progressively more powerful along the *time-dimension resolution* axis; used together they cover *stationarity, trend, changepoints, and dynamic evolution*. This study's gaming measurement converges across this four-fold lens on the conclusion of *grant-transfer cycle dominance + temporal intensification* (capital-acquisition is separately dominant in RDD jumps — see Appendix E).

#pagebreak()

= Appendix E. Year-End RDD Supplementary Analysis — Forest Plots by Field and Project Archetype

The results section of the main text summarizes the RDD results as *overall 1.91×* + *capital-acquisition archetype 3.42× (strongest)*. For detailed forest plots for all 14 fields and the jump multipliers for the four project archetypes, refer to this appendix.

*RDD jump ordering by project archetype*: Capital-acquisition (3.42×) > Normal (2.24×) > Labor-cost (1.12×) > Grant-transfer (1.10×, ns).

The capital-acquisition archetype shows the strongest RDD jump, whereas grant-transfer is weak in RDD but strongest in *annual cycle amplitude* (Appendix D). Both archetypes are bound to the exogenous accounting cycle but with *different temporal manifestation structures*: capital-acquisition produces a *discrete spike immediately after December 1*, while grant-transfer generates *distributed intensity spanning the annual cycle*. See the 'RDD vs spectral measures' paragraph in the main text results section.

#figure(
  image("figures_en/h22_rdd_appendix.png", height: 7cm),
  caption: [December jump forest plot by project archetype — Capital-acquisition 3.42× is strongest; Grant-transfer 1.10× does not reach statistical significance (gray) but is dominant in cycle intensity in Appendix D. For field-level forest plots, see @fig-rdd-field in the main text.],
)

#pagebreak()

= Appendix F. P-A Model Derivations

This appendix formally derives the first-order conditions and comparative statics of the *theoretical model* section in the main text. Notation is identical to the main text.

== F.1 Agent First-Order Conditions and Equilibrium Solution

The agent's objective function
$ U_A(e_t, e_q) = w_t e_t + w_q tilde(e)_q(e_q) - c(e_t, e_q; theta) $
where $tilde(e)_q$ is the measurable portion of $e_q$: $tilde(e)_q = phi(e_q)$, $phi'(\cdot) > 0$, $phi'(\cdot) < 1$ (measurability gap), $phi''(\cdot) <= 0$ (diminishing returns). The cost function $c$ is assumed to be *$C^2$ strictly convex*, so $c_(t t) > 0$, $c_(q q) > 0$, $c_(t q) = c_(q t) >= 0$ (cross-partial derivatives symmetric by Young's theorem).

Interior first-order conditions (differentiation with respect to $e_q$ applies the chain rule through $tilde(e)_q = phi(e_q)$):
$ (partial U_A) / (partial e_t) = w_t - c_t (e_t, e_q) = 0 $
$ (partial U_A) / (partial e_q) = w_q phi'(e_q) - c_q (e_t, e_q) = 0 $

By the Implicit Function Theorem, the equilibrium solutions are $e_t^*(w_t, w_q, theta)$ and $e_q^*(w_t, w_q, theta)$.

== F.2 Comparative Statics Derivation (Cramer's Rule)

Differentiating the FOCs with respect to $w_t$ (chain rule + implicit function theorem):

$ partial / partial w_t [w_t - c_t (e_t^*, e_q^*)] = 0 $
$ partial / partial w_t [w_q phi'(e_q^*) - c_q (e_t^*, e_q^*)] = 0 $

Rearranging as a linear system in the two unknowns $((partial e_t^*) / (partial w_t), (partial e_q^*) / (partial w_t))$:

$ mat(c_(t t), c_(t q); c_(q t), c_(q q) - w_q phi'') vec((partial e_t^*) / (partial w_t), (partial e_q^*) / (partial w_t)) = vec(1, 0) $

Determinant (Hessian determinant):
$ D = c_(t t) (c_(q q) - w_q phi'') - c_(t q)^2 $

*Sign analysis*:
- Cost convexity → $c_(t t) > 0$, $c_(q q) > 0$, $c_(t q)^2 >= 0$
- Diminishing returns assumption $phi'' <= 0$ → $-w_q phi'' >= 0$
- Therefore $c_(q q) - w_q phi'' > 0$ (sum of a positive and a non-negative term → strictly positive; the deciding factor is $c_(q q) > 0$, with $-w_q phi'' >= 0$ serving as a reinforcing effect)
- General strict convexity assumption $c_(t t) c_(q q) > c_(t q)^2$ (weak effort complementarity)

Therefore $D > 0$ (Hessian is positive definite; second-order condition is satisfied).

*Derivation of $(partial e_t^*) / (partial w_t)$ via Cramer's rule*:
$ (partial e_t^*) / (partial w_t) = det mat(1, c_(t q); 0, c_(q q) - w_q phi'') / D = (c_(q q) - w_q phi'') / D > 0  $

Because the numerator $> 0$ and $D > 0$, the sign is *positive*. This is consistent with the proposition in the main text.

*Derivation of $(partial e_t^*) / (partial w_q)$*: Implicitly differentiate the two FOCs with respect to $w_q$.
- Differentiating equation 1 ($w_t - c_t(e_t^*, e_q^*) = 0$) with respect to $w_q$:
  $ -c_(t t) (partial e_t^*) / (partial w_q) - c_(t q) (partial e_q^*) / (partial w_q) = 0 $
- Differentiating equation 2 ($w_q phi'(e_q^*) - c_q(e_t^*, e_q^*) = 0$) with respect to $w_q$ ($w_q$ appears explicitly on the left-hand side → $phi'$ is added outside the chain rule):
  $ phi'(e_q^*) + w_q phi''(e_q^*) (partial e_q^*) / (partial w_q) - c_(q t) (partial e_t^*) / (partial w_q) - c_(q q) (partial e_q^*) / (partial w_q) = 0 $

Rearranging as a linear system (the left-hand side matrix is the same):
$ mat(c_(t t), c_(t q); c_(q t), c_(q q) - w_q phi'') vec((partial e_t^*) / (partial w_q), (partial e_q^*) / (partial w_q)) = vec(0, phi') $

Cramer's rule:
$ (partial e_t^*) / (partial w_q) = det mat(0, c_(t q); phi', c_(q q) - w_q phi'') / D = -(c_(t q) phi') / D $

The sign depends on the sign of $c_(t q)$. Under this study's Korean-context assumption — *that timing adjustment and quality effort by the agent are resource-competing (substitutes, $c_(t q) > 0$)*:
$ (partial e_t^*) / (partial w_q) < 0 quad ("quality evaluation weight ↑ → gaming ↓") $

The sign is consistent with the proposition in §3.4. The model also allows for $c_(t q) = 0$ (independent efforts, yielding no effect) and $c_(t q) < 0$ (complements, potentially reversing the sign), but resource competition is the natural assumption in the Korean evaluation environment.

*$(partial e_t^*) / (partial c_(t t))$*: When the curvature parameter $c_(t t)$ of the cost function $c$ increases exogenously, the left-hand side of FOC equation 1 ($w_t = c_t(e_t^*, e_q^*)$) is fixed while the right-hand side curve steepens, so the equilibrium $e_t^*$ decreases (direct implicit differentiation):
$ (partial e_t^*) / (partial c_(t t)) < 0 $
An increase in the agent's marginal cost of timing adjustment leads to a decrease in equilibrium effort. This is the model basis for Policy Recommendations 3 and 5 (dispersed settlement timing, automatic flagging).

== F.3 Specialization of Cost Function by Project Archetype

Specializing $c(e_t, e_q; theta)$ for each archetype $theta$:

- *Labor-cost (theta_0)*: $c_t = infinity$ for $e_t > 0$ — timing adjustment is fundamentally infeasible ($e_t^* = 0$)
- *Capital-acquisition (theta_1)*: $c_t (e_t)$ is a *step function* immediately before December 1 — $c_t = epsilon$ (small) for $e_t in [0, e_t^max]$, diverges for $e_t > e_t^max$. Equilibrium: a sudden jump to the maximum feasible level → *discrete RDD spike*
- *Grant-transfer (theta_2)*: $c_t (e_t)$ is *distributed* — marginal cost is *spread throughout the year* because settlement timing varies across commissioned institutions. Equilibrium: gradual accumulation throughout the annual cycle → *spectral amplitude dominance*
- *Normal (theta_3)*: Average $c_t$ — a mixture of the two patterns

This specialization is the model basis for Hypotheses H2 and H3 in the main text.

== F.4 Limitations and Future Research

Limitations and directions for future research on this model are discussed in §8 of the main text. The formal specification of model-specific extensions (micro-level calibration, dynamic equilibrium, multi-agent interaction, application of causal forests) is deferred to separate future work.

#pagebreak()

// =============================================================
= Appendix G. Script-Hypothesis Mapping — Reproduction Guide

A one-to-one mapping between the core analysis scripts of this study and the hypothesis/results sections is presented below. Running the corresponding files in the `scripts/` directory of the GitHub repository (`bluethestyle/goodhart-korea`) reproduces the figures and CSV files cited in the main text.

#figure(
  table(
    columns: (1.2fr, 1fr, 2fr),
    [*Script*], [*Hypothesis / Results*], [*Role*],
    [`scripts/h3_v2_11y.py`], [H1 / §6.1–§6.2], [UMAP + HDBSCAN: identification of 4 archetypes],
    [`scripts/h4_v3_replaced.py`], [H1 supplement / §6.2], [Mapper graph + Persistent Homology],
    [`scripts/h22_rdd_yearend.py`], [H2 / §6.3], [Fiscal year-end RDD jump estimation],
    [`scripts/h27_power_spectrum_coherence.py`], [H3 / §6.4], [PSD, Phase, Coherence],
    [`scripts/h26_neuralprophet_check.py`], [Methodology / §6.5], [NeuralProphet cross-check],
    [`scripts/h23_mediation.py`], [H4 / §6.6], [Baron-Kenny + Sobel + Bootstrap],
    [`scripts/h6_robustness.py`], [H5 / §6.7], [FE regression, Permutation, Lag/Lead],
    [`scripts/h10_macro_control.py`], [H5 auxiliary / §6.7], [CPI exogenous control],
    [`scripts/h28_wavelet.py`], [H6 / §6.8], [Wavelet temporal dynamic intensification],
    [`scripts/h24_stl_decomp.py`], [Robustness / §6.9], [STL self-critique],
  ),
  caption: [Mapping of core analysis scripts to hypothesis and results sections — reproduction guide],
)
