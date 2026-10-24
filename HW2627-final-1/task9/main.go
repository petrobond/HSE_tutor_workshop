// Задание 9. Мини-банкомат
package main

import (
	"fmt"
	"os"
	"strconv"
)

func readInt(prompt string) int {
	for {
		fmt.Print(prompt)
		var s string
		if _, err := fmt.Scan(&s); err != nil {
			fmt.Println("Ошибка: не удалось прочитать ввод")
			os.Exit(1)
		}
		x, err := strconv.Atoi(s)
		if err != nil {
			fmt.Println("Ошибка: нужно ввести целое число")
			continue
		}
		return x
	}
}

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

func main() {
	balance := readFloat("Введите начальный баланс: ")

	if balance < 0 {
		fmt.Println("Ошибка: баланс не может быть отрицательным")
		return
	}

	for {
		fmt.Println()
		fmt.Println("1 - посмотреть баланс")
		fmt.Println("2 - пополнить баланс")
		fmt.Println("3 - снять средства")
		fmt.Println("0 - выход")

		choice := readInt("Выберите действие: ")

		switch choice {
		case 1:
			fmt.Printf("Текущий баланс: %.2f\n", balance)
		case 2:
			amount := readFloat("Сумма пополнения: ")
			if amount <= 0 {
				fmt.Println("Ошибка: сумма должна быть больше нуля")
				continue
			}
			balance += amount
			fmt.Printf("Баланс пополнен. Текущий баланс: %.2f\n", balance)
		case 3:
			amount := readFloat("Сумма снятия: ")
			if amount <= 0 {
				fmt.Println("Ошибка: сумма должна быть больше нуля")
				continue
			}
			if amount > balance {
				fmt.Println("Ошибка: недостаточно средств на балансе")
				continue
			}
			balance -= amount
			fmt.Printf("Средства сняты. Текущий баланс: %.2f\n", balance)
		case 0:
			fmt.Println("До свидания")
			return
		default:
			fmt.Println("Ошибка: неизвестное действие")
		}
	}
}
