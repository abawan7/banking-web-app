let container = document.getElementById('container')

toggle = () => {
	container.classList.toggle('sign-in')
	container.classList.toggle('sign-up')
}

setTimeout(() => {
	container.classList.add('sign-in')
}, 200)


function myalert() {
	alert("User Not Found");
}

function dateSelected(sender, args) {
    var selectedDate = args._selectedDate;
    var formattedDate = selectedDate.getFullYear() + '-' + (selectedDate.getMonth() + 1) + '-' + selectedDate.getDate();
    document.getElementById('<%= SelectedDate.ClientID %>').value = formattedDate;
    __doPostBack('<%= SelectedDate.ClientID %>', '');
}

// prevent default behavior of calendar control
function preventDefaultBehavior() {
    return false;
}

// handle calendar selection changed event
function handleSelectionChanged() {
    // perform necessary actions
    alert("Date selected!");

    // prevent default behavior
    return false;
}

// attach event listeners to calendar control
var calendar = document.getElementById('<%= Calendar1.ClientID %>');
calendar.onclick = preventDefaultBehavior;
calendar.onchange = handleSelectionChanged;