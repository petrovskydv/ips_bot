const nowDate = new Date()
const monthNames = ['Январь', 'Ферваль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь', 'Январь', 'Ферваль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
// 2021-07-19
function fetchMonths(startMonth=nowDate.getMonth(), startYear=nowDate.getUTCFullYear()) {
  let buttons = [],
      firstRow = [],
      secondRow = [],
      thirdRow = [],
      fourthRow = [],
      currentMonth = 0,
      currentYear = startYear;
  for (let i = startMonth; i < startMonth + 12; i++) {
    currentMonth = i;
    if (i > 11) {currentYear = startYear + 1; currentMonth = i - 12}
    let monthButton = {
        'buttonText': `${monthNames[currentMonth]} ${currentYear}`,
        'buttonValue': `^${currentMonth}-${currentYear}`
    }
    if (i <= startMonth + 2){
      firstRow.push(monthButton)
    }
    if (startMonth + 2 < i && i <= startMonth + 5){
      secondRow.push(monthButton)
    }
    if (startMonth + 5 < i && i <= startMonth + 8){
      thirdRow.push(monthButton)
    }
    if (startMonth + 8 < i && i <= startMonth + 11){
      fourthRow.push(monthButton)
    }
  }
  buttons.push(firstRow, secondRow, thirdRow, fourthRow)
  return buttons
}
// alert(fetchMonths())

function daysInMonth (month, year) {
    return new Date(year, month + 1, 0).getDate();
}

function dayInWeek (day, month, year) {
    return new Date(year, month, day).getDay() != 0 ? new Date(year, month, day).getDay() : 7;
}

function fetchMonthDays(month=nowDate.getMonth(), year=nowDate.getUTCFullYear()) {
  let buttons = [],
      startDay = 1,
      daysInThisMonth = daysInMonth(month, year),
      monthText = `${monthNames[month]} ${year}[сменить месяц]`;

  alert('DAYS!!!')
  alert(daysInThisMonth)

  buttons.push([{'buttonText': monthText, 'buttonValue': 'back'}]);
  let dateCounter = 0
  if (month == nowDate.getMonth()) {startDay = nowDate.getDate()}
  let startDayInWeek = dayInWeek(startDay, month, year),
      availableDaysInMonth = daysInThisMonth - startDay + 1,
      firstRow = [],
      lastRow = [],
      lastDayInWeek = dayInWeek(daysInMonth(month, year), month, year);

  if (availableDaysInMonth <= 7) {
    for (let j = 1; j <= 7; j++) {
        if (j < startDayInWeek) {
          let button = {
            'buttonText': '',
            'buttonValue': '',
            'buttonActive': false
          }
          firstRow.push(button)
        } else if (j > lastDayInWeek) {
          let button = {
            'buttonText': '',
            'buttonValue': '',
            'buttonActive': false
          }
          firstRow.push(button)
        } else {
          dateCounter = dateCounter + 1
          let button = {
            'buttonText': `${dateCounter + startDay - 1}`,
            'buttonValue': `_${dateCounter + startDay - 1}-${month}-${year}`,
            'buttonActive': true
          }
          firstRow.push(button)
        }
        buttons.push(firstRow)
        return buttons
      }
  }

  for (let j = 1; j <= 7; j++) {
        if (j < startDayInWeek) {
          let button = {
            'buttonText': '',
            'buttonValue': '',
            'buttonActive': false
          }
        firstRow.push(button)
        } else {
          dateCounter = dateCounter + 1
          let button = {
            'buttonText': `${dateCounter + startDay - 1}`,
            'buttonValue': `_${dateCounter + startDay - 1}-${month}-${year}`,
            'buttonActive': true
          }
        firstRow.push(button)
        }
      }
      buttons.push(firstRow)

  for (let j = 1; j <= 7; j++) {
    if (j > lastDayInWeek) {
      let button = {
        'buttonText': '',
        'buttonValue': '',
        'buttonActive': false
      }
      lastRow.push(button)
    } else {
      dateCounter = dateCounter + 1
      let button = {
        'buttonText': `${daysInMonth(month, year) - (lastDayInWeek - j)}`,
        'buttonValue': `_${daysInMonth(month, year) - (lastDayInWeek - j)}-${month}-${year}`,
        'buttonActive': true
      }
      lastRow.push(button)
    }
  }

  let leftedDates = availableDaysInMonth - dateCounter;
  dateCounter = dateCounter - lastDayInWeek
  for (let i = 0; i < leftedDates / 7; i++){
    let row = [];
    for (let j = 1; j <= 7; j++) {
      dateCounter = dateCounter + 1
      let button = {
          'buttonText': `${dateCounter}`,
          'buttonValue': `_${dateCounter}-${month}-${year}`,
          'buttonActive': true
      }
      row.push(button)
    }
    buttons.push(row)
  }
  alert(leftedDates)
  buttons.push(lastRow)
  return buttons
}

alert(fetchMonthDays(4, 2021))
// alert(dayInWeek(daysInMonth(1,2021), 1, 2021)).
// alert(dayInWeek(22, 1, 2021))
// alert(daysInMonth(6,2021))