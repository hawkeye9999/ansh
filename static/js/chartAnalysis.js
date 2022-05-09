$(document).ready(() => {
    console.log(chartData)
    const labels = new Set()
    let n = chartData.quiz_ids.length
    $(".barChartWrapArea").width(n * 250)
    let allScores = {topScores:new Array(n).fill(0),avgScores:new Array(n).fill(0),myScores:new Array(n).fill(0)}
    chartData.quiz_ids.forEach((q_id,index) => {
        let count = 0
        chartData.scores.forEach((score,sub_index) => {
            if(score.quiz_id == q_id){
                count += 1
                labels.add(score.q_title)
                allScores.topScores[index] = Number(score.user_score > allScores.topScores[index] ? score.user_score: allScores.topScores[index])
                if(score.user === chartData.svv){
                    allScores.myScores[index] = Number(score.user_score)
                }
                allScores.avgScores[index] += Number(score.user_score )
                console.log("avgScore",allScores.avgScores)
                console.log("myScore",allScores.myScores)
                console.log("topScore",allScores.topScores)
                console.log("count",count)
            }
        })
        let avg = allScores.avgScores[index] / count
        allScores.avgScores[index] = Math.round((avg + Number.EPSILON) * 100) / 100

    })

    
    var barCtx = document.getElementById("barChart").getContext("2d");
    console.log(allScores,"ALLLL")
    const barData = {
        labels: [...labels],
        datasets:[
            {
                label: "My Score",
                backgroundColor: "#1a8cff",
                data:allScores.myScores,
                barThickness: 5,
            },
            {
                label: "Avg Score",
                backgroundColor: "#58d8a3",
                data:allScores.avgScores,
                barThickness: 5,
            },
            {
                label: "Top Score",
                backgroundColor: "#E91E63",
                data:allScores.topScores,
                barThickness: 5,
            }
        ]
    }



      var myBarChart = new Chart(barCtx, {
        type: 'bar',
        data: barData,
        plugins: [{
            beforeInit: function(chart, options) {
              chart.legend.afterFit = function() {
                this.height = this.height + 50;
              };
            }
          }],
        
        options: {
            responsive:true,
            maintainAspectRatio:false,

            tooltips: {
                titleFontSize: 24,
                bodyFontSize: 19
              },
            
            legend: {
                labels: {
                    fontSize:24 ,
                    fontColor:"#222"
                }
            },
            scales: {
                xAxes:[{
                    // categoryPercentage: 0.1,
                    barPercentage: 1,
                    barThickness:70,
                    barHeight:70,
                    gridLines:{
                      color:"#cb2d3e",
                      zeroLineColor:"#cb2d3e"
                    },
                    ticks: {
                        fontSize: 24
                    }
                  }],                
                yAxes: [{
                    ticks: {
                        min: 0,
                        fontSize: 24,
                        fontColor:"#222"
                    },
                    gridLines: {
                        display:false
                    }   
                }]
            }
        }
    });
    
    // DOUGHNUT CHART
    let labels_ = []
    let data_ = []
    let colors = ['#58d8a3','#E91E63','#f6e84e','#57c7d4','#0f1531','#198ae3']
    let bgColors = []
    chartData.subject_scores.forEach((score,index) => {
        let subject_parts = score.q_sub.split(" ")

        if(subject_parts.length > 1){
            let subject = ''
            subject_parts.forEach((parts) => {
                subject += parts.slice(0,1)
            })
            labels_.push(subject)
        }else{
            labels_.push(score.q_sub)
        }
        
        data_.push(score.avg_score)
        bgColors.push(colors[index])
    })

    var spiralCtx = document.getElementById("spiralChart").getContext("2d");

    const spiralData = {
        labels: labels_,
        datasets: [{
          label: 'My First Dataset',
          data: data_,
          backgroundColor: bgColors,
          hoverOffset: 4
        }]
      };

      console.log(spiralData,"spiral")
    
      var doughtnutCHart = new Chart(spiralCtx, {
        type: 'doughnut',
        data: spiralData,
        options:{
            responsive:true,
            cutoutPercentage: 60,
            maintainAspectRatio:false,
            legend: {
                labels: {
                    fontSize:20 ,
                    fontColor:"#222"
                }
            },
            tooltips: {
                titleFontSize: 20,
                bodyFontSize: 20
              },
        },
        plugins: [{
            beforeInit: function(chart, options) {
              chart.legend.afterFit = function() {
                this.height = this.height + 50;
              };
            }
          }],

      })

})