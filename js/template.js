var api_url = 'https://machine-translation-comparator.herokuapp.com/';
function makeAsyncGetRequest(path) {
	return new Promise(function (resolve, reject) {
		axios.get(api_url + path).then(
			(response) => {
				var returnObj = response.data;
				console.log('Async Get Request: ' + path);
				resolve(returnObj);
			},
			(error) => {
				reject(error);
			}
		);
	});
}

function makeAsyncPostRequest(path, queryObject) {
	return new Promise(function (resolve, reject) {
		axios.post(api_url + path, queryObject).then(
			(response) => {
				var returnObj = response.data;
				console.log('Async Post Request');
				resolve(returnObj);
			},
			(error) => {
				reject(error);
			}
		);
	});
}

function makeGetRequest(path) {
	axios.get(api_url + path).then(
		(response) => {
			var returnObj = response.data;
			return returnObj;
		},
		(error) => {
			return error;
		}
	);
}

function makePostRequest(path, queryObject) {
	axios.post(api_url + path, queryObject).then(
		(response) => {
			var returnObj = response.data;
			return returnObj;
		},
		(error) => {
			return error;
		}
	);
}
