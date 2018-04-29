const print = console.log;

function funcA () {
	print('func A is called!');
}

function main() {
	let a = funcA;
	a();
}

main();
