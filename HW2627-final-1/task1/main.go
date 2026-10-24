// Задание 1. Калькулятор с проверкой
package main

import (
	"fmt"
	"os"
	"strconv"
)

func readFloat(prompt string) float64 {
	for {
		fmt.Print(prompt)
		var s string
		if _, err := fmt.Scan(&s); err != nil {
			fmt.Println("Ошибка: не удалось прочитать ввод")
			os.Exit(1)
		}
		x, err := strconv.ParseFloat(s, 64)
		if err != nil {
			fmt.Println("Ошибка: нужно ввести число")
			continue
		}
		return x
	}
}

func readOp() string {
	for {
		fmt.Print("Введите операцию (+ - * /): ")
		var op string
		if _, err := fmt.Scan(&op); err != nil {
			fmt.Println("Ошибка: не удалось прочитать ввод")
			os.Exit(1)
		}
		if op == "+" || op == "-" || op == "*" || op == "/" {
			return op
		}
		fmt.Println("Ошибка: неизвестная операция")
	}
}

func main() {
	for {
		a := readFloat("Введите первое число: ")
		op := readOp()
		b := readFloat("Введите второе число: ")

		switch op {
		case "+":
			fmt.Printf("Результат: %.2f\n", a+b)
		case "-":
			fmt.Printf("Результат: %.2f\n", a-b)
		case "*":
			fmt.Printf("Результат: %.2f\n", a*b)
		case "/":
			if b == 0 {
				fmt.Println("Ошибка: деление на ноль невозможно")
			} else {
				fmt.Printf("Результат: %.2f\n", a/b)
			}
		}

		fmt.Print("Повторить? (д/н): ")
		var answer string
		fmt.Scan(&answer)
		if answer != "д" {
			break
		}
		fmt.Println()
	}
}
