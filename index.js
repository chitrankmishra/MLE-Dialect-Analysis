function initialize() {
	document.getElementById('search-div').style.display = 'none';
	document.getElementById('efficiency-charts').style.display = 'none';
	document.getElementById('clash-error').style.display = 'none';
	document.getElementById('phrase-error').style.display = 'none';
	document.getElementById('translator-error').style.display = 'none';
	document.getElementById('lang-error').style.display = 'none';
}

async function displaySearchSpace() {
	document.getElementById('search-div').style.display = 'block';
	document.getElementById('efficiency-charts').style.display = 'none';
	await addLangOptions(
		document.getElementsByClassName('from-lang')[0],
		'from-lang'
	);
	await addLangOptions(
		document.getElementsByClassName('to-lang')[0],
		'to-lang'
	);
	window.scrollBy(0, 800);
}

async function addLangOptions(element, id) {
	selectText = '<select class="form-control select" id="' + id + '">\n ';
	response = await makeAsyncGetRequest('/get-languages/');
	languageCodes = response.result;

	for (x in languageCodes) {
		selectText +=
			'<option value="' + languageCodes[x] + '">' + x + '</option>\n';
	}
	selectText += '</select>\n';

	element.innerHTML = selectText;
}

async function addTranslatorOptions(element, id) {
	selectText = '<select class="form-control select" id="' + id + '">\n ';
	response = await makeAsyncGetRequest('/get-translators/');
	translators = response.result;

	for (x in translators) {
		if (x == 'DeepL Translate') continue;
		selectText += '<option value="' + x + '">' + x + '</option>\n';
	}
	selectText += '</select>\n';

	element.innerHTML = selectText;
}

async function searchPhrase() {
	document.getElementById('clash-error').style.display = 'none';
	document.getElementById('phrase-error').style.display = 'none';
	phrase = document.getElementById('phrase-input').value;
	src = document.getElementById('from-lang').value;
	trg = document.getElementById('to-lang').value;
	error_flag = 0;

	if (src == trg) {
		document.getElementById('clash-error').style.display = 'block';
		error_flag = 1;
	}
	if (!phrase) {
		document.getElementById('phrase-error').style.display = 'block';
		error_flag = 1;
	}
	if (error_flag) return;

	console.log('Translating "' + phrase + '" from ' + src + ' to ' + trg);
	resultDiv = document.getElementById('result-div');
	resultDiv.innerHTML =
		'<div class="row center">    <span class="highlight2"  id="loading"> LOADING ...</span></div>';

	var i = 1;
	var loading = setInterval(function () {
		text = 'LOADING';
		var t = 0;
		while (t <= i) {
			text += '.';
			t++;
		}
		document.getElementById('loading').innerHTML = text;
		i = (i + 1) % 4;
	}, 500);

	response = await makeAsyncGetRequest('/get-translators/');
	translators = response.result;

	for (instance in translators) {
		response = await makeAsyncGetRequest(
			'/' + translators[instance] + '/' + src + '/' + trg + '/' + phrase + '/'
		);

		console.log(response.result);

		resultDiv.innerHTML += appendResults(
			instance,
			translators[instance],
			response.result
		);
	}
	clearInterval(loading);
	document.getElementById('loading').innerHTML = '';
}

function appendResults(labelname, classname, result) {
	text = '<div class="row result-instance">\n    <div class="col-sm-2">\n';
	text += '<img class="translator-icon" src="images/' + classname + '.png" />';
	text += '<label class="elem-label">' + labelname + ':</label></div>';
	text +=
		'<div class="col-sm-10" >\n <textarea class="form-control ' +
		classname +
		'" id="result" readonly>';
	text += result['translation'];
	text += '</textarea></div></div>';
	text += '<div class="row">    <div class="col-sm-2"></div>';
	text +=
		'<div class="col-sm-5">Scraped from: <a href="' +
		result['url'] +
		'">' +
		labelname +
		' Source</a></div>';
	text +=
		'<div class="col-sm-5">Response Time:<span class="highlight2"> ' +
		result['calltime'] +
		' seconds</span></div>';
	text += '</div>';

	return text;
}

async function displayEfficiencyCharts() {
	document.getElementById('search-div').style.display = 'none';
	document.getElementById('efficiency-charts').style.display = 'block';

	await addLangOptions(
		document.getElementsByClassName('languages')[0],
		'effi-lang'
	);
	await addTranslatorOptions(
		document.getElementsByClassName('translator-names')[0],
		'effi-trans'
	);
	window.scrollBy(0, 800);
}

async function compareTranslators() {
	document.getElementById('translator-error').style.display = 'none';
	trans = document.getElementById('effi-trans').value;
	if (trans == '') {
		document.getElementById('translator-error').style.display = 'block';
		return;
	}
	document.getElementById('translator-error').style.display = 'none';
	space = trans.indexOf(' ');
	name = trans.substring(0, space);

	var resultDiv = document.getElementById('effi-results');
	resultDiv.innerHTML =
		'<div class="row center">    <span class="highlight2"  id="loading2"> LOADING ...</span></div>';

	var i = 1;
	var loading = setInterval(function () {
		text = 'LOADING';
		var t = 0;
		while (t <= i) {
			text += '.';
			t++;
		}
		document.getElementById('loading2').innerHTML = text;
		i = (i + 1) % 4;
	}, 500);

	response = await makeAsyncGetRequest('/get-efficiency-tuple/');
	data = response.result;
	response = await makeAsyncGetRequest('/get-languages/');
	languages = response.result;

	// console.log(data, languages);
	var resultDiv = document.getElementById('effi-results');
	var dataset = {};
	for (x in languages) {
		dataset[languages[x]] = {};
	}

	for (x in languages) {
		for (y in data) {
			if (languages[x] == data[y]['From']) {
				// console.log(languages[x], data[y]['From'], y);
				dataset[languages[x]][data[y]['To']] = data[y].Efficiency[name] * 100;
			}
		}
	}
	// console.log(dataset);
	resultDiv.innerHTML = '';
	divtext = '';
	divtext += '<div class="row main-option">\n';
	divtext +=
		'<img class="translator-icon" src="images/' +
		name.toLowerCase() +
		'-translate.png"/>	';
	divtext += '<span class="highlight2">' + name + ' Translate: </span></div>';

	resultDiv.innerHTML = divtext;
	for (x in dataset) {
		divtext = '';
		divtext += '<div class="row sub-option">';
		divtext += '<span class="highlight"> From ';
		for (l in languages) if (languages[l] == x) divtext += l;
		divtext += ' to: </span>	</div>';
		resultDiv.innerHTML += divtext;

		for (y in dataset[x]) {
			divtext = '';
			trgname = '';
			if (y == x) continue;
			for (l in languages) if (languages[l] == y) trgname = l;
			divtext += appendProgressBars(y, trgname, dataset[x][y].toFixed(2));
			// console.log(x, dataset[x][y]);
			resultDiv.innerHTML += divtext;
		}
		resultDiv.innerHTML += '<hr>';
	}

	clearInterval(loading);
}

function appendProgressBars(trg, trgname, percent) {
	var text = '';
	text += '<div class="row bars">	';
	text += '<div class="col-sm-2">' + trgname + ':</div>';
	text += '<div class="col-sm-10"><div class="progress">';
	text +=
		'	<div class="progress-bar progress-bar-striped progress-bar-animated bg-' +
		trg +
		'"';
	text +=
		'	role="progressbar"	aria-valuenow="' +
		percent +
		'" aria-valuemin="0"	aria-valuemax="100"	style="width: ' +
		percent +
		'%">';
	text += ' ' + percent + '%</div></div></div></div>';
	return text;
}

async function compareLanguage() {
	document.getElementById('lang-error').style.display = 'none';
	lang = document.getElementById('effi-lang').value;
	if (lang == '') {
		document.getElementById('lang-error').style.display = 'block';
		return;
	}
	document.getElementById('lang-error').style.display = 'none';

	var resultDiv = document.getElementById('effi-results');
	resultDiv.innerHTML =
		'<div class="row center">    <span class="highlight2"  id="loading2"> LOADING ...</span></div>';

	var i = 1;
	var loading = setInterval(function () {
		text = 'LOADING';
		var t = 0;
		while (t <= i) {
			text += '.';
			t++;
		}
		document.getElementById('loading2').innerHTML = text;
		i = (i + 1) % 4;
	}, 500);

	response = await makeAsyncGetRequest('/get-efficiency-tuple/');
	data = response.result;
	response = await makeAsyncGetRequest('/get-languages/');
	languages = response.result;

	name = '';
	for (l in languages) if (lang == languages[l]) name = l;
	// console.log(data, languages);
	var resultDiv = document.getElementById('effi-results');

	// console.log(dataset);
	resultDiv.innerHTML = '';
	divtext = '';
	divtext += '<div class="row main-option">\n';
	divtext +=
		'<img class="translator-icon" src="images/' +
		name.toLowerCase() +
		'.png"/>	';
	divtext += '<span class="highlight2">From ' + name + ' </span></div>';
	resultDiv.innerHTML = divtext;

	for (l in languages) {
		divtext = '';
		if (l == name) continue;
		divtext += '<div class="row sub-option">';
		divtext += '<span class="highlight">To ' + l + ': </span></div>';
		resultDiv.innerHTML += divtext;

		for (y in data) {
			if (data[y]['From'] == lang && data[y]['To'] == languages[l]) {
				divtext = '';
				trgname = '';
				for (t in data[y]['Efficiency'])
					divtext += appendProgressBars(
						t,
						t,
						(data[y]['Efficiency'][t] * 100).toFixed(2)
					);
				// console.log(x, dataset[x][y]);
				resultDiv.innerHTML += divtext;
			}
		}
		resultDiv.innerHTML += '<hr>';
	}

	clearInterval(loading);
}
