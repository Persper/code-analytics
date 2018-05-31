const print = console.log;

function funcA () {
	print('func A is called!');
}

function main() {
	let a = funcA;
	let b = function funcB () {
		funcA();
		print('func B is called!');
	};
	let c = a;
	b();
	c();
}

main();
