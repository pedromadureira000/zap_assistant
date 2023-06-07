const mask = (selector) => {
    function setMask(target) {
      let matrix = '+###############';

      maskList.forEach(item => {
          let code = item.code.replace(/[\s#\-)(]/g, '');
          let phone = target.value.replace(/[\s#\-)(]/g, '');
          if (phone.includes(code)) {
            console.log(phone, code);
            matrix = item.code;
          }
      });

      let i = 0;
      let val = target.value.replace(/\D/g, '');
      target.value = matrix.replace(/(?!\+)./g, function(a) {
          return /[#\d]/.test(a) && i < val.length ? val.charAt(i++) : i >= val.length ? '' : a;
      });
    }

    let input = document.querySelector(selector);

    const removePhoneMask = () => {
      input.value = input.value.replace(/\D/g, '')
    };
    const form = document.querySelector('#form');
    form.addEventListener("submit", removePhoneMask);

    if (!input.value){
      input.value = '+'
    }
    else {
      setMask(input);
      setMask(input);
    }
    input.addEventListener('input', (ev) => setMask(ev.target));
    input.addEventListener('focus', (ev) => setMask(ev.target));
    input.addEventListener('blur', (ev) => setMask(ev.target));
};
