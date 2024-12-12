document.addEventListener("DOMContentLoaded", () => {
    try {
        const biotypeData = JSON.parse(document.getElementById("biotype-data").textContent);
        if (!biotypeData || biotypeData.length === 0) {
            console.warn("No biotype data available to render the chart.");
            return;
        }

        const labels = biotypeData.map((item) => item.biotype);
        const percentages = biotypeData.map((item) => item.percentage);

        const ctx = document.getElementById("biotype-pie-chart").getContext("2d");
        new Chart(ctx, {
            type: "pie",
            data: {
                labels: labels,
                datasets: [
                    {
                        data: percentages,
                        backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0"],
                        hoverBackgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0"],
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "right",
                        labels: {
                            boxWidth: 20,
                            padding: 15,
                        },
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const value = context.raw || 0;
                                return `${context.label}: ${value.toFixed(2)}%`;
                            },
                        },
                    },
                },
                layout: {
                    padding: {
                        top: 10,
                        right: 50,
                        bottom: 10,
                        left: 500,
                    },
                },
            },
        });
    } catch (error) {
        console.error("Error creating pie chart:", error);
    }
});