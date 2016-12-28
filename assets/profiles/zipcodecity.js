const cityFromZipCode = zipCode => (
  new Promise((resolve, reject) => {
    fetch(`https://fraktguide.bring.no/fraktguide/api/postalCode.json?country=no&pnr=${zipCode}`, { mode: 'cors' })
    // To JSON
    .then(response => response.json())
    // JSON looks like { result: 'city', ...}
    .then(json => json.result)
    // Resolve promise with city name
    .then(resolve)
    // Otherwise reject
    .catch(reject);
  })
);

export default cityFromZipCode;
