// Theme toggle: persist selection in localStorage and apply dark-mode class
(function(){
	const toggle = document.getElementById('theme-toggle');
	const body = document.body;
	const KEY = 'grammar_theme';

	function applyTheme(theme){
		if(theme === 'dark'){
			body.classList.add('dark-mode');
			if(toggle) toggle.textContent = '☀️';
		} else {
			body.classList.remove('dark-mode');
			if(toggle) toggle.textContent = '🌙';
		}
	}

	// Read saved preference or system preference
	let saved = null;
	try{ saved = localStorage.getItem(KEY); }catch(e){}
	if(saved){ applyTheme(saved); }
	else if(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches){
		applyTheme('dark');
	} else {
		applyTheme('light');
	}

	if(toggle){
		toggle.addEventListener('click', ()=>{
			const isDark = body.classList.contains('dark-mode');
			const next = isDark ? 'light' : 'dark';
			applyTheme(next);
			try{ localStorage.setItem(KEY, next); }catch(e){}
			// small fade animation
			body.classList.add('theme-transition');
			window.setTimeout(()=> body.classList.remove('theme-transition'), 400);
		});
	}
})();