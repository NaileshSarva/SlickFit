"""Flet desktop UI for PeakForge.

Lets the user log training sessions and performance tests, fit their
personalized Banister model parameters, run the optimal taper search
for an upcoming event, and view the resulting form curve.

Run with:  python main.py
"""

from __future__ import annotations

import datetime as dt
import io

import flet as ft
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .fitting import fit_parameters
from .models import PerformanceTest, TrainingSession
from .optimizer import GAConfig, TaperConstraints, find_optimal_taper
from .simulation import simulate
from .storage import PeakForgeStore


def _plot_form_curve(dates: list[str], fitness, fatigue, performance) -> bytes:
    fig, ax = plt.subplots(figsize=(7, 3.2))
    x = range(len(dates))
    ax.plot(x, fitness, label="Fitness (CTL)", color="#1f77b4")
    ax.plot(x, fatigue, label="Fatigue (ATL)", color="#d62728")
    ax.plot(x, performance, label="Performance", color="#2ca02c", linewidth=2)
    ax.set_xlabel("Day")
    ax.set_ylabel("Arbitrary load units")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_title("Projected Form Curve")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    return buf.getvalue()


def main(page: ft.Page) -> None:
    page.title = "PeakForge"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 24

    store = PeakForgeStore()

    status_text = ft.Text("", color=ft.colors.GREEN_700)
    chart_image = ft.Image(width=680, height=320, fit=ft.ImageFit.CONTAIN)
    taper_output = ft.Text("")

    # -- Session logging ---------------------------------------------
    date_field = ft.TextField(label="Date (YYYY-MM-DD)", width=180,
                               value=dt.date.today().isoformat())
    duration_field = ft.TextField(label="Duration (min)", width=140, value="60")
    intensity_field = ft.TextField(label="Intensity (RPE 1-10)", width=160, value="6")

    def add_session(_):
        try:
            duration = float(duration_field.value)
            intensity = float(intensity_field.value)
        except ValueError:
            status_text.value = "Duration and intensity must be numbers."
            status_text.color = ft.colors.RED_600
            page.update()
            return
        load = duration * intensity
        store.add_session(TrainingSession(date=date_field.value, load=load))
        status_text.value = f"Session logged: {date_field.value} — load {load:.1f}"
        status_text.color = ft.colors.GREEN_700
        page.update()

    # -- Performance test logging --------------------------------------
    perf_date_field = ft.TextField(label="Test date (YYYY-MM-DD)", width=180,
                                    value=dt.date.today().isoformat())
    perf_score_field = ft.TextField(label="Performance score", width=160, value="")

    def add_performance(_):
        try:
            score = float(perf_score_field.value)
        except ValueError:
            status_text.value = "Performance score must be a number."
            status_text.color = ft.colors.RED_600
            page.update()
            return
        store.add_performance_test(PerformanceTest(date=perf_date_field.value, score=score))
        status_text.value = f"Performance test logged: {perf_date_field.value} — score {score}"
        status_text.color = ft.colors.GREEN_700
        page.update()

    # -- Fit parameters --------------------------------------------------
    def fit_and_plot(_):
        sessions = store.list_sessions()
        tests = store.list_performance_tests()

        if len(sessions) < 5:
            status_text.value = "Log at least 5 training sessions before fitting."
            status_text.color = ft.colors.RED_600
            page.update()
            return
        if len(tests) < 3:
            status_text.value = "Log at least 3 performance tests before fitting."
            status_text.color = ft.colors.RED_600
            page.update()
            return

        session_dates = [s.date for s in sessions]
        loads = [s.load for s in sessions]
        date_index = {d: i for i, d in enumerate(session_dates)}

        obs_days, obs_scores = [], []
        for t in tests:
            if t.date in date_index:
                obs_days.append(date_index[t.date])
                obs_scores.append(t.score)

        if len(obs_days) < 3:
            status_text.value = "Performance test dates must match logged session dates."
            status_text.color = ft.colors.RED_600
            page.update()
            return

        params = fit_parameters(loads, obs_days, obs_scores)
        store.save_params(params)

        sim = simulate(loads, params.k1, params.k2, params.tau1, params.tau2, params.p0)
        chart_image.src_base64 = None
        img_bytes = _plot_form_curve(session_dates, sim["fitness"], sim["fatigue"], sim["performance"])
        import base64
        chart_image.src_base64 = base64.b64encode(img_bytes).decode()

        status_text.value = (
            f"Fitted: k1={params.k1:.3f}  k2={params.k2:.3f}  "
            f"tau1={params.tau1:.0f}d  tau2={params.tau2:.0f}d  p0={params.p0:.2f} "
            f"(residual={params.residual_error:.2f})"
        )
        status_text.color = ft.colors.GREEN_700
        page.update()

    # -- Optimal taper search --------------------------------------------
    event_days_field = ft.TextField(label="Days until event", width=160, value="21")

    def run_taper(_):
        params = store.latest_params()
        if params is None:
            status_text.value = "Fit your parameters first."
            status_text.color = ft.colors.RED_600
            page.update()
            return

        sessions = store.list_sessions()
        loads_history = [s.load for s in sessions]

        try:
            days = int(event_days_field.value)
        except ValueError:
            status_text.value = "Days until event must be an integer."
            status_text.color = ft.colors.RED_600
            page.update()
            return

        result = find_optimal_taper(
            loads_history, days,
            params.k1, params.k2, params.tau1, params.tau2, params.p0,
            constraints=TaperConstraints(),
            config=GAConfig(generations=120),
        )

        rounded = [round(v, 1) for v in result.best_loads]
        taper_output.value = (
            f"Predicted peak performance on event day: {result.predicted_peak_performance:.2f}\n"
            f"Recommended daily loads for the next {days} day(s):\n{rounded}"
        )

        full_loads = loads_history + result.best_loads
        sim = simulate(full_loads, params.k1, params.k2, params.tau1, params.tau2, params.p0)
        import base64
        img_bytes = _plot_form_curve(
            [str(i) for i in range(len(full_loads))],
            sim["fitness"], sim["fatigue"], sim["performance"],
        )
        chart_image.src_base64 = base64.b64encode(img_bytes).decode()

        status_text.value = "Optimal taper computed."
        status_text.color = ft.colors.GREEN_700
        page.update()

    # -- Layout ------------------------------------------------------------
    page.add(
        ft.Text("PeakForge", size=30, weight=ft.FontWeight.BOLD),
        ft.Text("Physiological Performance-Simulation & Optimal Taper Engine",
                size=14, italic=True, color=ft.colors.GREY_700),
        ft.Divider(),

        ft.Text("1. Log a training session", size=18, weight=ft.FontWeight.BOLD),
        ft.Row([date_field, duration_field, intensity_field,
                ft.ElevatedButton("Add session", on_click=add_session)]),

        ft.Text("2. Log a performance test", size=18, weight=ft.FontWeight.BOLD),
        ft.Row([perf_date_field, perf_score_field,
                ft.ElevatedButton("Add test", on_click=add_performance)]),

        ft.Text("3. Fit your personalized model", size=18, weight=ft.FontWeight.BOLD),
        ft.ElevatedButton("Fit parameters & show form curve", on_click=fit_and_plot),

        ft.Text("4. Compute optimal taper", size=18, weight=ft.FontWeight.BOLD),
        ft.Row([event_days_field, ft.ElevatedButton("Run optimizer", on_click=run_taper)]),
        taper_output,

        ft.Divider(),
        status_text,
        chart_image,
    )


def run() -> None:
    ft.app(target=main)


if __name__ == "__main__":
    run()
