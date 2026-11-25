from futility import Futility

script = "<+>>>--<<[+++++]"

vm = Futility(script)
vm.run()

print(vm.memory)
print(vm.cycles)
