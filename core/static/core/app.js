
document.addEventListener("DOMContentLoaded", () => {

    // Mobile sidebar toggle
    const toggle = document.getElementById("menuToggle");
    const side = document.getElementById("sidebar");

    if (toggle && side) {
        toggle.addEventListener("click", () => {
            side.classList.toggle("open");
        });
    }

    // Dashboard chart data
    const d = window.dashboardData;

    // Risk distribution doughnut chart
    const risk = document.getElementById("riskChart");

    if (risk && d && typeof Chart !== "undefined") {
        new Chart(risk, {
            type: "doughnut",
            data: {
                labels: ["Low risk", "Medium risk", "High risk"],
                datasets: [{
                    data: d.risks,
                    backgroundColor: [
                        "#35d39a",
                        "#f5b84b",
                        "#fa6878"
                    ],
                    borderWidth: 0,
                    hoverOffset: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "76%",
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: "#071321",
                        titleColor: "#fff",
                        bodyColor: "#c6d5e8"
                    }
                }
            }
        });
    }

    // Academic performance bar chart
    const perf = document.getElementById("performanceChart");

    if (perf && d && typeof Chart !== "undefined") {
        new Chart(perf, {
            type: "bar",
            data: {
                labels: d.labels,
                datasets: [
                    {
                        label: "Internal marks",
                        data: d.marks,
                        backgroundColor: "#22c7df",
                        borderRadius: 5,
                        barThickness: 12
                    },
                    {
                        label: "Attendance",
                        data: d.attendance,
                        backgroundColor: "#9877ff",
                        borderRadius: 5,
                        barThickness: 12
                    },
                    {
                        label: "Assignment score",
                        data: d.assignments,
                        backgroundColor: "#35d39a",
                        borderRadius: 5,
                        barThickness: 12
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: "index",
                    intersect: false
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: {
                            color: "#a3b5ca",
                            font: { size: 11 }
                        },
                        border: { color: "#2a3b53" }
                    },
                    y: {
                        min: 0,
                        max: 100,
                        grid: { color: "#1d3047" },
                        ticks: {
                            color: "#a3b5ca",
                            callback: value => value + "%",
                            font: { size: 11 }
                        },
                        border: { display: false }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: "#c3d1e2",
                            usePointStyle: true,
                            boxWidth: 8,
                            font: { size: 11 }
                        }
                    },
                    tooltip: {
                        backgroundColor: "#071321"
                    }
                }
            }
        });
    }

    // Risk Analysis page data
    const riskData = window.riskAnalysisData;

    // Overall risk category chart
    const categoryCanvas =
        document.getElementById("riskCategoryBar");

    if (categoryCanvas && riskData && typeof Chart !== "undefined") {
        new Chart(categoryCanvas, {
            type: "bar",
            data: {
                labels: riskData.labels,
                datasets: [{
                    label: "Students",
                    data: riskData.values,
                    backgroundColor: [
                        "#35d39a",
                        "#f5b84b",
                        "#fa6878"
                    ],
                    borderRadius: 8,
                    maxBarThickness: 72
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: "#071321",
                        titleColor: "#fff",
                        bodyColor: "#c6d5e8"
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: {
                            color: "#a3b5ca",
                            font: { size: 12 }
                        },
                        border: { color: "#2a3b53" }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: "#1d3047" },
                        ticks: {
                            precision: 0,
                            color: "#a3b5ca",
                            font: { size: 11 }
                        },
                        border: { display: false }
                    }
                }
            }
        });
    }

    // Department-wise risk chart
    const departmentCanvas =
        document.getElementById("departmentRiskBar");

    if (departmentCanvas && riskData && typeof Chart !== "undefined") {
        new Chart(departmentCanvas, {
            type: "bar",
            data: {
                labels: riskData.departments,
                datasets: [
                    {
                        label: "Low risk",
                        data: riskData.departmentLow,
                        backgroundColor: "#35d39a",
                        borderRadius: 4
                    },
                    {
                        label: "Medium risk",
                        data: riskData.departmentMedium,
                        backgroundColor: "#f5b84b",
                        borderRadius: 4
                    },
                    {
                        label: "High risk",
                        data: riskData.departmentHigh,
                        backgroundColor: "#fa6878",
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            color: "#c3d1e2",
                            usePointStyle: true,
                            boxWidth: 8,
                            padding: 16,
                            font: { size: 11 }
                        }
                    },
                    tooltip: {
                        backgroundColor: "#071321"
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                        grid: { display: false },
                        ticks: {
                            color: "#a3b5ca",
                            font: { size: 11 }
                        },
                        border: { color: "#2a3b53" }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        grid: { color: "#1d3047" },
                        ticks: {
                            precision: 0,
                            color: "#a3b5ca",
                            font: { size: 11 }
                        },
                        border: { display: false }
                    }
                }
            }
        });
    }

});

